#!/usr/bin/env python3
"""
Build Matrix Generator for OpenSSL CI
Intelligently generates build matrix based on changes and optimization strategies
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any
from pathlib import Path


class BuildMatrixGenerator:
    """Generates optimized build matrix for OpenSSL CI"""
    
    def __init__(self):
        self.platforms = {
            'ubuntu-22.04': {
                'runs-on': 'ubuntu-22.04',
                'profiles': ['linux-gcc-release', 'linux-gcc-debug', 'linux-fips'],
                'compilers': ['gcc-11', 'gcc-12', 'clang-15']
            },
            'ubuntu-20.04': {
                'runs-on': 'ubuntu-20.04',
                'profiles': ['linux-gcc-release', 'linux-gcc-debug'],
                'compilers': ['gcc-9', 'gcc-10']
            },
            'windows-2022': {
                'runs-on': 'windows-2022',
                'profiles': ['windows-msvc'],
                'compilers': ['msvc-2022']
            },
            'macos-12': {
                'runs-on': 'macos-12',
                'profiles': ['macos-clang'],
                'compilers': ['clang-14', 'clang-15']
            }
        }
        
        self.build_scopes = {
            'full': {
                'description': 'Full build - all platforms and configurations',
                'platforms': ['ubuntu-22.04', 'ubuntu-20.04', 'windows-2022', 'macos-12'],
                'profiles': ['linux-gcc-release', 'linux-gcc-debug', 'linux-fips', 'windows-msvc', 'macos-clang'],
                'test_enabled': True
            },
            'test': {
                'description': 'Test-focused build - validation and testing only',
                'platforms': ['ubuntu-22.04'],
                'profiles': ['linux-gcc-debug'],
                'test_enabled': True,
                'options': ['enable_unit_test=True', 'enable_demos=True']
            },
            'provider': {
                'description': 'Provider build - provider-specific components',
                'platforms': ['ubuntu-22.04', 'windows-2022'],
                'profiles': ['linux-gcc-release', 'windows-msvc'],
                'test_enabled': False,
                'options': ['enable_demos=False']
            },
            'minimal': {
                'description': 'Minimal build - essential checks only',
                'platforms': ['ubuntu-22.04'],
                'profiles': ['linux-gcc-release'],
                'test_enabled': False,
                'options': ['enable_unit_test=False', 'enable_demos=False']
            }
        }
    
    def generate_matrix(self, source_repo: str, source_sha: str, build_scope: str,
                       core_changes: int, config_changes: int, test_changes: int,
                       provider_changes: int) -> Dict[str, Any]:
        """Generate build matrix based on context"""
        
        print(f"🔧 Generating build matrix for scope: {build_scope}")
        print(f"   Core changes: {core_changes}")
        print(f"   Config changes: {config_changes}")
        print(f"   Test changes: {test_changes}")
        print(f"   Provider changes: {provider_changes}")
        
        # Get build scope configuration
        scope_config = self.build_scopes.get(build_scope, self.build_scopes['minimal'])
        
        # Generate matrix entries
        matrix_entries = []
        
        for platform in scope_config['platforms']:
            platform_config = self.platforms[platform]
            
            for profile in scope_config['profiles']:
                if profile in platform_config['profiles']:
                    # Generate base matrix entry
                    entry = {
                        'platform': platform,
                        'profile': profile,
                        'source_repo': source_repo,
                        'source_sha': source_sha,
                        'build_scope': build_scope,
                        'test_enabled': scope_config.get('test_enabled', False),
                        'options': self._generate_options(profile, scope_config, core_changes, config_changes)
                    }
                    
                    # Add compiler variants for Linux
                    if platform.startswith('ubuntu'):
                        for compiler in platform_config['compilers']:
                            compiler_entry = entry.copy()
                            compiler_entry['compiler'] = compiler
                            compiler_entry['matrix_key'] = f"{platform}-{profile}-{compiler}"
                            matrix_entries.append(compiler_entry)
                    else:
                        entry['matrix_key'] = f"{platform}-{profile}"
                        matrix_entries.append(entry)
        
        # Optimize matrix based on changes
        optimized_entries = self._optimize_matrix(matrix_entries, core_changes, config_changes, test_changes, provider_changes)
        
        return {
            'include': optimized_entries,
            'total_jobs': len(optimized_entries),
            'build_scope': build_scope,
            'optimization_applied': len(optimized_entries) < len(matrix_entries)
        }
    
    def _generate_options(self, profile: str, scope_config: Dict, core_changes: int, config_changes: int) -> List[str]:
        """Generate Conan options based on profile and changes"""
        options = []
        
        # Base options from scope config
        if 'options' in scope_config:
            options.extend(scope_config['options'])
        
        # Profile-specific options
        if profile == 'linux-fips':
            options.extend(['fips=True', 'enable_unit_test=True'])
        elif profile == 'linux-gcc-debug':
            options.extend(['enable_unit_test=True', 'enable_demos=True', 'enable_trace=True'])
        elif profile == 'linux-gcc-release':
            options.extend(['enable_unit_test=False', 'enable_demos=False'])
        
        # Change-based optimizations
        if core_changes > 0:
            # Core changes require full validation
            options.extend(['enable_unit_test=True'])
        
        if config_changes > 0:
            # Config changes require testing
            options.extend(['enable_unit_test=True'])
        
        return options
    
    def _optimize_matrix(self, entries: List[Dict], core_changes: int, config_changes: int, 
                        test_changes: int, provider_changes: int) -> List[Dict]:
        """Optimize matrix based on change patterns"""
        
        # If only test changes, focus on test profiles
        if test_changes > 0 and core_changes == 0 and config_changes == 0:
            print("   🧪 Test-only changes detected, optimizing for test profiles")
            return [entry for entry in entries if 'debug' in entry['profile']]
        
        # If only provider changes, focus on provider-relevant platforms
        if provider_changes > 0 and core_changes == 0:
            print("   🔌 Provider-only changes detected, optimizing for provider platforms")
            return [entry for entry in entries if entry['platform'] in ['ubuntu-22.04', 'windows-2022']]
        
        # If config changes only, focus on release profiles
        if config_changes > 0 and core_changes == 0:
            print("   ⚙️ Config-only changes detected, optimizing for release profiles")
            return [entry for entry in entries if 'release' in entry['profile']]
        
        # If core changes, include FIPS builds
        if core_changes > 0:
            print("   🚀 Core changes detected, including FIPS builds")
            return entries
        
        # Default: return all entries
        return entries
    
    def generate_cache_strategy(self, matrix: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cache optimization strategy"""
        
        cache_strategy = {
            'cache_keys': [],
            'retention_policies': {},
            'warming_strategies': []
        }
        
        # Generate cache keys for each matrix entry
        for entry in matrix['include']:
            cache_key = self._generate_cache_key(entry)
            cache_strategy['cache_keys'].append(cache_key)
        
        # Set retention policies based on build scope
        if matrix['build_scope'] == 'full':
            cache_strategy['retention_policies'] = {
                'development': '7d',
                'staging': '30d',
                'production': '365d'
            }
        else:
            cache_strategy['retention_policies'] = {
                'development': '3d',
                'staging': '7d',
                'production': '30d'
            }
        
        # Generate warming strategies
        cache_strategy['warming_strategies'] = [
            {
                'profile': 'linux-gcc-release',
                'priority': 'high',
                'frequency': 'daily'
            },
            {
                'profile': 'linux-fips',
                'priority': 'medium',
                'frequency': 'weekly'
            }
        ]
        
        return cache_strategy
    
    def _generate_cache_key(self, entry: Dict[str, Any]) -> str:
        """Generate cache key for matrix entry"""
        key_parts = [
            entry['platform'],
            entry['profile'],
            entry['source_sha'][:8]  # Short SHA
        ]
        
        if 'compiler' in entry:
            key_parts.append(entry['compiler'])
        
        return '-'.join(key_parts)
    
    def save_matrix(self, matrix: Dict[str, Any], output_file: str):
        """Save matrix to file"""
        with open(output_file, 'w') as f:
            json.dump(matrix, f, indent=2)
        
        print(f"✅ Build matrix saved to {output_file}")
        print(f"   Total jobs: {matrix['total_jobs']}")
        print(f"   Optimization applied: {matrix['optimization_applied']}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate OpenSSL build matrix')
    parser.add_argument('--source-repo', required=True, help='Source repository')
    parser.add_argument('--source-sha', required=True, help='Source SHA')
    parser.add_argument('--build-scope', required=True, help='Build scope')
    parser.add_argument('--core-changes', type=int, default=0, help='Number of core changes')
    parser.add_argument('--config-changes', type=int, default=0, help='Number of config changes')
    parser.add_argument('--test-changes', type=int, default=0, help='Number of test changes')
    parser.add_argument('--provider-changes', type=int, default=0, help='Number of provider changes')
    parser.add_argument('--output-format', choices=['json', 'yaml'], default='json', help='Output format')
    parser.add_argument('--output-file', help='Output file path')
    
    args = parser.parse_args()
    
    # Generate matrix
    generator = BuildMatrixGenerator()
    matrix = generator.generate_matrix(
        source_repo=args.source_repo,
        source_sha=args.source_sha,
        build_scope=args.build_scope,
        core_changes=args.core_changes,
        config_changes=args.config_changes,
        test_changes=args.test_changes,
        provider_changes=args.provider_changes
    )
    
    # Generate cache strategy
    cache_strategy = generator.generate_cache_strategy(matrix)
    matrix['cache_strategy'] = cache_strategy
    
    # Output matrix
    if args.output_file:
        generator.save_matrix(matrix, args.output_file)
    else:
        if args.output_format == 'json':
            print(json.dumps(matrix, indent=2))
        else:
            import yaml
            print(yaml.dump(matrix, default_flow_style=False))


if __name__ == '__main__':
    main()