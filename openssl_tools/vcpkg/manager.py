"""
vcpkg Package Manager

Manages vcpkg package installation and dependency resolution.
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .detector import VcpkgDetector


class VcpkgManager:
    """Manages vcpkg package operations."""
    
    def __init__(self, vcpkg_root: Optional[str] = None):
        self.detector = VcpkgDetector()
        self.vcpkg_root = vcpkg_root or self.detector.detect_vcpkg_root()
        self.vcpkg_exe = self.detector.get_vcpkg_executable()
        
    def install_package(self, package: str, features: List[str] = None, 
                       triplet: str = None) -> bool:
        """Install a vcpkg package with optional features."""
        if not self.vcpkg_exe:
            return False
        
        # Build package specification
        package_spec = package
        if features:
            package_spec += f"[{','.join(features)}]"
        
        # Build command
        cmd = [self.vcpkg_exe, "install", package_spec]
        
        if triplet:
            cmd.extend(["--triplet", triplet])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def install_from_manifest(self, manifest_path: str, triplet: str = None) -> bool:
        """Install packages from a vcpkg.json manifest file."""
        if not self.vcpkg_exe:
            return False
        
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")
        
        # Build command
        cmd = [self.vcpkg_exe, "install", "--manifest-root", os.path.dirname(manifest_path)]
        
        if triplet:
            cmd.extend(["--triplet", triplet])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def list_installed_packages(self, triplet: str = None) -> List[Dict[str, str]]:
        """List installed vcpkg packages."""
        if not self.vcpkg_exe:
            return []
        
        cmd = [self.vcpkg_exe, "list"]
        
        if triplet:
            cmd.extend(["--triplet", triplet])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return []
            
            packages = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        packages.append({
                            "name": parts[0],
                            "version": parts[1],
                            "triplet": parts[2] if len(parts) > 2 else triplet or "default"
                        })
            
            return packages
        except (subprocess.TimeoutExpired, Exception):
            return []
    
    def search_package(self, package_name: str) -> List[Dict[str, str]]:
        """Search for available vcpkg packages."""
        if not self.vcpkg_exe:
            return []
        
        cmd = [self.vcpkg_exe, "search", package_name]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return []
            
            packages = []
            for line in result.stdout.strip().split('\n'):
                if line.strip() and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        packages.append({
                            "name": parts[0],
                            "version": parts[1],
                            "description": ' '.join(parts[2:]) if len(parts) > 2 else ""
                        })
            
            return packages
        except (subprocess.TimeoutExpired, Exception):
            return []
    
    def create_manifest(self, packages: List[Dict[str, Any]], 
                       output_path: str) -> bool:
        """Create a vcpkg.json manifest file."""
        manifest = {
            "name": "openssl-dependencies",
            "version": "1.0.0",
            "description": "OpenSSL build dependencies",
            "dependencies": []
        }
        
        for package in packages:
            dep = {"name": package["name"]}
            if "version" in package:
                dep["version>="] = package["version"]
            if "features" in package and package["features"]:
                dep["features"] = package["features"]
            manifest["dependencies"].append(dep)
        
        try:
            with open(output_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            return True
        except Exception:
            return False
    
    def install_openssl_dependencies(self, fips_mode: bool = False, 
                                   triplet: str = None) -> bool:
        """Install OpenSSL and its dependencies via vcpkg."""
        packages = [
            {
                "name": "openssl",
                "features": ["tools"]
            },
            {
                "name": "zlib"
            }
        ]
        
        if fips_mode:
            # Add FIPS-specific packages if available
            packages.append({
                "name": "openssl",
                "features": ["fips"]
            })
        
        # Create temporary manifest
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            manifest_path = f.name
            self.create_manifest(packages, manifest_path)
        
        try:
            success = self.install_from_manifest(manifest_path, triplet)
            return success
        finally:
            # Clean up temporary file
            try:
                os.unlink(manifest_path)
            except:
                pass
    
    def get_package_info(self, package_name: str, triplet: str = None) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific package."""
        if not self.vcpkg_exe:
            return None
        
        cmd = [self.vcpkg_exe, "show", package_name]
        
        if triplet:
            cmd.extend(["--triplet", triplet])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return None
            
            info = {}
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            return info
        except (subprocess.TimeoutExpired, Exception):
            return None
    
    def is_package_installed(self, package_name: str, triplet: str = None) -> bool:
        """Check if a package is installed."""
        installed = self.list_installed_packages(triplet)
        return any(pkg["name"] == package_name for pkg in installed)
    
    def remove_package(self, package_name: str, triplet: str = None) -> bool:
        """Remove a vcpkg package."""
        if not self.vcpkg_exe:
            return False
        
        cmd = [self.vcpkg_exe, "remove", package_name]
        
        if triplet:
            cmd.extend(["--triplet", triplet])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False