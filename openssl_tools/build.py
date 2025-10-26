"""
OpenSSL Build Manager

Manages OpenSSL builds with vcpkg integration support.
"""

import os
import subprocess
import platform
from typing import Dict, Any, Optional, List
from .vcpkg import VcpkgIntegration, VcpkgManager


class OpenSSLBuildManager:
    """Manages OpenSSL builds with optional vcpkg integration."""
    
    def __init__(self, use_vcpkg: bool = True, vcpkg_root: Optional[str] = None):
        self.use_vcpkg = use_vcpkg
        self.vcpkg_integration = VcpkgIntegration(vcpkg_root) if use_vcpkg else None
        self.vcpkg_manager = VcpkgManager(vcpkg_root) if use_vcpkg else None
        
    def setup_build_environment(self, build_dir: str, 
                              fips_mode: bool = False) -> Dict[str, Any]:
        """Setup build environment for OpenSSL."""
        env_info = {
            "use_vcpkg": self.use_vcpkg,
            "fips_mode": fips_mode,
            "build_dir": build_dir,
            "environment_vars": {},
            "cmake_toolchain": None,
            "dependencies": []
        }
        
        if self.use_vcpkg and self.vcpkg_integration:
            # Setup vcpkg integration
            env_vars = self.vcpkg_integration.setup_environment()
            env_info["environment_vars"].update(env_vars)
            
            # Install OpenSSL dependencies
            if self.vcpkg_integration.manager:
                success = self.vcpkg_integration.manager.install_openssl_dependencies(fips_mode)
                if success:
                    env_info["dependencies"].append("openssl (via vcpkg)")
                    env_info["dependencies"].append("zlib (via vcpkg)")
            
            # Setup CMake toolchain
            if self.vcpkg_integration.vcpkg_root:
                cmake_file = os.path.join(build_dir, "vcpkg-openssl.cmake")
                if self.vcpkg_integration.setup_cmake_integration(cmake_file):
                    env_info["cmake_toolchain"] = cmake_file
        
        return env_info
    
    def configure_openssl(self, source_dir: str, build_dir: str, 
                         options: Dict[str, Any] = None) -> bool:
        """Configure OpenSSL build."""
        if not options:
            options = {}
        
        # Default configuration options
        config_options = {
            "shared": True,
            "fPIC": True,
            "fips": False,
            "no_threads": False,
            "no_asm": False
        }
        config_options.update(options)
        
        # Build Configure command
        configure_cmd = self._build_configure_command(source_dir, build_dir, config_options)
        
        try:
            # Change to source directory
            original_cwd = os.getcwd()
            os.chdir(source_dir)
            
            # Run Configure
            result = subprocess.run(configure_cmd, shell=True, capture_output=True, text=True)
            
            # Restore original directory
            os.chdir(original_cwd)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _build_configure_command(self, source_dir: str, build_dir: str, 
                               options: Dict[str, Any]) -> str:
        """Build the Configure command for OpenSSL."""
        # Determine target platform
        target = self._get_configure_target()
        
        # Build command
        cmd_parts = [
            "./Configure",
            target,
            f"--prefix={build_dir}",
            f"--openssldir={build_dir}"
        ]
        
        # Add options
        if options.get("fips"):
            cmd_parts.append("enable-fips")
        
        if not options.get("shared"):
            cmd_parts.append("no-shared")
        
        if options.get("no_threads"):
            cmd_parts.append("no-threads")
        
        if options.get("no_asm"):
            cmd_parts.append("no-asm")
        
        return " ".join(cmd_parts)
    
    def _get_configure_target(self) -> str:
        """Get the Configure target for the current platform."""
        os_name = platform.system()
        arch = platform.machine()
        
        target_map = {
            ("Linux", "x86_64"): "linux-x86_64",
            ("Linux", "x86"): "linux-x86",
            ("Windows", "x86_64"): "VC-WIN64A",
            ("Windows", "x86"): "VC-WIN32",
            ("Darwin", "arm64"): "darwin64-arm64-cc",
            ("Darwin", "x86_64"): "darwin64-x86_64-cc",
        }
        
        return target_map.get((os_name, arch), "linux-x86_64")
    
    def build_openssl(self, build_dir: str, parallel_jobs: int = None) -> bool:
        """Build OpenSSL."""
        if not parallel_jobs:
            parallel_jobs = self._get_optimal_job_count()
        
        try:
            # Change to build directory
            original_cwd = os.getcwd()
            os.chdir(build_dir)
            
            # Run make
            make_cmd = f"make -j{parallel_jobs}"
            result = subprocess.run(make_cmd, shell=True, capture_output=True, text=True)
            
            # Restore original directory
            os.chdir(original_cwd)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def install_openssl(self, build_dir: str, install_dir: str) -> bool:
        """Install OpenSSL to the target directory."""
        try:
            # Change to build directory
            original_cwd = os.getcwd()
            os.chdir(build_dir)
            
            # Run make install
            install_cmd = f"make install DESTDIR={install_dir}"
            result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
            
            # Restore original directory
            os.chdir(original_cwd)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _get_optimal_job_count(self) -> int:
        """Get optimal number of parallel jobs for building."""
        import multiprocessing
        
        cpu_count = multiprocessing.cpu_count() or 1
        
        # In CI environments, use all available cores
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            return cpu_count
        
        # Locally, reserve some cores for system responsiveness
        reserved = 1 if cpu_count > 2 else 0
        return max(1, cpu_count - reserved)
    
    def test_openssl(self, build_dir: str) -> bool:
        """Test OpenSSL build."""
        try:
            # Change to build directory
            original_cwd = os.getcwd()
            os.chdir(build_dir)
            
            # Run tests
            test_cmd = "make test"
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
            
            # Restore original directory
            os.chdir(original_cwd)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def get_build_info(self) -> Dict[str, Any]:
        """Get build information and status."""
        info = {
            "use_vcpkg": self.use_vcpkg,
            "vcpkg_available": False,
            "openssl_installed": False,
            "platform": {
                "os": platform.system(),
                "arch": platform.machine(),
                "python_version": platform.python_version()
            }
        }
        
        if self.use_vcpkg and self.vcpkg_integration:
            validation = self.vcpkg_integration.validate_integration()
            info["vcpkg_available"] = validation["vcpkg_available"]
            info["openssl_installed"] = validation["openssl_installed"]
            info["vcpkg_errors"] = validation["errors"]
        
        return info