"""
vcpkg Detection Utilities

Detects vcpkg installation and provides environment setup.
"""

import os
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict, Any


class VcpkgDetector:
    """Detects and validates vcpkg installation."""
    
    def __init__(self):
        self.vcpkg_root: Optional[str] = None
        self.vcpkg_executable: Optional[str] = None
        self.triplet: Optional[str] = None
        
    def detect_vcpkg_root(self) -> Optional[str]:
        """Detect vcpkg installation root directory."""
        # Check environment variables first
        env_vars = ["VCPKG_ROOT", "VCPKG_INSTALLATION_ROOT"]
        for var in env_vars:
            root = os.getenv(var)
            if root and os.path.exists(root):
                if self._validate_vcpkg_root(root):
                    self.vcpkg_root = root
                    return root
        
        # Check common installation paths
        possible_paths = self._get_common_paths()
        for path in possible_paths:
            if os.path.exists(path) and self._validate_vcpkg_root(path):
                self.vcpkg_root = path
                return path
                
        return None
    
    def _get_common_paths(self) -> list:
        """Get common vcpkg installation paths based on platform."""
        home = os.path.expanduser("~")
        system = platform.system().lower()
        
        if system == "windows":
            return [
                os.path.join(home, "vcpkg"),
                os.path.join(home, ".vcpkg"),
                "C:\\vcpkg",
                "C:\\tools\\vcpkg",
                "C:\\Program Files\\vcpkg"
            ]
        elif system == "darwin":  # macOS
            return [
                os.path.join(home, "vcpkg"),
                os.path.join(home, ".vcpkg"),
                "/usr/local/vcpkg",
                "/opt/vcpkg"
            ]
        else:  # Linux and others
            return [
                os.path.join(home, "vcpkg"),
                os.path.join(home, ".vcpkg"),
                "/usr/local/vcpkg",
                "/opt/vcpkg",
                "/usr/share/vcpkg"
            ]
    
    def _validate_vcpkg_root(self, root: str) -> bool:
        """Validate that the given path is a valid vcpkg installation."""
        vcpkg_exe = os.path.join(root, "vcpkg")
        if os.name == "nt":  # Windows
            vcpkg_exe += ".exe"
        
        return os.path.exists(vcpkg_exe) and os.path.isfile(vcpkg_exe)
    
    def get_vcpkg_executable(self) -> Optional[str]:
        """Get the path to the vcpkg executable."""
        if not self.vcpkg_root:
            self.detect_vcpkg_root()
        
        if not self.vcpkg_root:
            return None
            
        vcpkg_exe = os.path.join(self.vcpkg_root, "vcpkg")
        if os.name == "nt":  # Windows
            vcpkg_exe += ".exe"
            
        if os.path.exists(vcpkg_exe):
            self.vcpkg_executable = vcpkg_exe
            return vcpkg_exe
            
        return None
    
    def detect_triplet(self, os_name: str = None, arch: str = None) -> str:
        """Detect the appropriate vcpkg triplet for the current platform."""
        if not os_name:
            os_name = platform.system().lower()
        if not arch:
            arch = platform.machine().lower()
        
        # Map Conan settings to vcpkg triplets
        os_map = {
            "windows": "windows",
            "linux": "linux",
            "darwin": "osx",
            "macos": "osx"
        }
        
        arch_map = {
            "x86_64": "x64",
            "amd64": "x64", 
            "x86": "x86",
            "i386": "x86",
            "armv8": "arm64",
            "aarch64": "arm64",
            "armv7": "arm",
            "arm": "arm"
        }
        
        vcpkg_os = os_map.get(os_name, "linux")
        vcpkg_arch = arch_map.get(arch, "x64")
        
        # Handle debug builds
        triplet = f"{vcpkg_os}-{vcpkg_arch}"
        
        # Windows debug builds use different triplet
        if os_name == "windows" and os.getenv("VCPKG_DEFAULT_TRIPLET", "").endswith("-debug"):
            triplet += "-debug"
            
        self.triplet = triplet
        return triplet
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables needed for vcpkg integration."""
        if not self.vcpkg_root:
            self.detect_vcpkg_root()
        
        if not self.vcpkg_root:
            return {}
        
        env_vars = {
            "VCPKG_ROOT": self.vcpkg_root,
            "CMAKE_TOOLCHAIN_FILE": os.path.join(
                self.vcpkg_root, "scripts", "buildsystems", "vcpkg.cmake"
            )
        }
        
        if self.triplet:
            env_vars["VCPKG_DEFAULT_TRIPLET"] = self.triplet
            env_vars["VCPKG_DEFAULT_HOST_TRIPLET"] = self.triplet
        
        return env_vars
    
    def is_vcpkg_available(self) -> bool:
        """Check if vcpkg is available and functional."""
        if not self.vcpkg_root:
            self.detect_vcpkg_root()
        
        if not self.vcpkg_root:
            return False
            
        vcpkg_exe = self.get_vcpkg_executable()
        if not vcpkg_exe:
            return False
        
        # Test vcpkg functionality
        try:
            result = subprocess.run(
                [vcpkg_exe, "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def get_vcpkg_info(self) -> Dict[str, Any]:
        """Get comprehensive vcpkg information."""
        info = {
            "available": False,
            "root": None,
            "executable": None,
            "triplet": None,
            "environment_vars": {}
        }
        
        if self.detect_vcpkg_root():
            info["available"] = self.is_vcpkg_available()
            info["root"] = self.vcpkg_root
            info["executable"] = self.get_vcpkg_executable()
            info["triplet"] = self.detect_triplet()
            info["environment_vars"] = self.get_environment_variables()
        
        return info