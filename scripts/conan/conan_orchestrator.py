#!/usr/bin/env python3
"""
Conan Orchestrator - Cross-platform Python-based Conan development tool
Master orchestrator for all Conan operations across platforms
"""

import os
import sys
import subprocess
import json
import yaml
import platform
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import argparse
import logging
from dataclasses import dataclass
from enum import Enum
import venv
import importlib.util

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Platform(Enum):
    """Supported platforms"""
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"

class BuildType(Enum):
    """Build types"""
    DEBUG = "debug"
    RELEASE = "release"

@dataclass
class ConanProfile:
    """Conan profile configuration"""
    name: str
    os: str = "Linux"
    arch: str = "x86_64"
    compiler: str = "gcc"
    compiler_version: str = "11"
    compiler_libcxx: str = "libstdc++11"
    build_type: str = "Release"
    generator: str = "Ninja"
    extra_conf: Dict[str, str] = None

    def __post_init__(self):
        if self.extra_conf is None:
            self.extra_conf = {}

class ConanOrchestrator:
    """Cross-platform Conan orchestrator"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conan_dir = project_root / "conan-dev"
        self.profiles_dir = self.conan_dir / "profiles"
        self.venv_dir = self.conan_dir / "venv"
        self.cache_dir = self.conan_dir / "cache"
        self.artifacts_dir = self.conan_dir / "artifacts"
        
        # Platform detection
        self.platform = self._detect_platform()
        self.python_executable = self._get_python_executable()
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Initialize profiles
        self.profiles = self._load_profiles()
        
    def _detect_platform(self) -> Platform:
        """Detect the current platform"""
        system = platform.system().lower()
        if system == "linux":
            return Platform.LINUX
        elif system == "windows":
            return Platform.WINDOWS
        elif system == "darwin":
            return Platform.MACOS
        else:
            logger.warning(f"Unknown platform: {system}, defaulting to Linux")
            return Platform.LINUX
    
    def _get_python_executable(self) -> Path:
        """Get the Python executable path"""
        if self.venv_dir.exists():
            if self.platform == Platform.WINDOWS:
                venv_python = self.venv_dir / "Scripts" / "python.exe"
            else:
                venv_python = self.venv_dir / "bin" / "python"
            
            if venv_python.exists():
                return venv_python
        
        return Path(sys.executable)
    
    def _get_conan_executable(self) -> Path:
        """Get the Conan executable path"""
        if self.venv_dir.exists():
            if self.platform == Platform.WINDOWS:
                conan_exe = self.venv_dir / "Scripts" / "conan.exe"
            else:
                conan_exe = self.venv_dir / "bin" / "conan"
            
            if conan_exe.exists():
                return conan_exe
        
        # Fallback to system conan
        return Path("conan")
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist"""
        directories = [
            self.conan_dir,
            self.profiles_dir,
            self.cache_dir,
            self.artifacts_dir,
            self.conan_dir / "locks",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_profiles(self) -> Dict[str, ConanProfile]:
        """Load available Conan profiles"""
        profiles = {}
        
        # Default profiles for all platforms
        default_profiles = {
            "linux-gcc11": ConanProfile(
                name="linux-gcc11",
                os="Linux",
                arch="x86_64",
                compiler="gcc",
                compiler_version="11",
                compiler_libcxx="libstdc++11",
                build_type="Release",
                generator="Ninja",
                extra_conf={
                    "tools.system.package_manager:mode": "install",
                    "tools.system.package_manager:sudo": "True"
                }
            ),
            "linux-clang15": ConanProfile(
                name="linux-clang15",
                os="Linux",
                arch="x86_64",
                compiler="clang",
                compiler_version="15",
                compiler_libcxx="libstdc++11",
                build_type="Release",
                generator="Ninja",
                extra_conf={
                    "tools.system.package_manager:mode": "install",
                    "tools.system.package_manager:sudo": "True"
                }
            ),
            "windows-msvc2022": ConanProfile(
                name="windows-msvc2022",
                os="Windows",
                arch="x86_64",
                compiler="msvc",
                compiler_version="193",
                compiler_libcxx="dynamic",
                build_type="Release",
                generator="Visual Studio 17 2022"
            ),
            "macos-clang14": ConanProfile(
                name="macos-clang14",
                os="Macos",
                arch="x86_64",
                compiler="apple-clang",
                compiler_version="14",
                compiler_libcxx="libc++",
                build_type="Release",
                generator="Xcode"
            ),
            "debug": ConanProfile(
                name="debug",
                os="Linux",  # Will be overridden
                arch="x86_64",
                compiler="gcc",
                compiler_version="11",
                compiler_libcxx="libstdc++11",
                build_type="Debug",
                generator="Ninja"
            )
        }
        
        # Load from files if they exist
        for profile_file in self.profiles_dir.glob("*.profile"):
            try:
                profile_data = self._parse_profile_file(profile_file)
                profiles[profile_data["name"]] = ConanProfile(**profile_data)
            except Exception as e:
                logger.warning(f"Failed to load profile {profile_file}: {e}")
        
        # Add defaults if not loaded from files
        for name, profile in default_profiles.items():
            if name not in profiles:
                profiles[name] = profile
        
        return profiles
    
    def _parse_profile_file(self, profile_file: Path) -> Dict[str, Any]:
        """Parse a Conan profile file"""
        profile_data = {"name": profile_file.stem}
        
        # Set defaults
        defaults = {
            "os": "Linux",
            "arch": "x86_64", 
            "compiler": "gcc",
            "compiler_version": "11",
            "compiler_libcxx": "libstdc++11",
            "build_type": "Release",
            "generator": "Ninja"
        }
        
        # Apply defaults
        for key, value in defaults.items():
            profile_data[key] = value
        
        with open(profile_file, 'r') as f:
            current_section = None
            for line in f:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                elif '=' in line and current_section:
                    key, value = line.split('=', 1)
                    if current_section == "settings":
                        if key == "os":
                            profile_data["os"] = value
                        elif key == "arch":
                            profile_data["arch"] = value
                        elif key == "compiler":
                            profile_data["compiler"] = value
                        elif key == "compiler.version":
                            profile_data["compiler_version"] = value
                        elif key == "compiler.libcxx":
                            profile_data["compiler_libcxx"] = value
                        elif key == "build_type":
                            profile_data["build_type"] = value
                    elif current_section == "conf":
                        if "extra_conf" not in profile_data:
                            profile_data["extra_conf"] = {}
                        profile_data["extra_conf"][key] = value
        
        return profile_data
    
    def setup_environment(self, force: bool = False) -> bool:
        """Set up the Conan development environment"""
        try:
            logger.info("🚀 Setting up Conan development environment...")
            
            # Create virtual environment first
            if not self.venv_dir.exists() or force:
                self._create_virtual_environment()
            
            # Update Python executable path after creating venv
            self.python_executable = self._get_python_executable()
            
            # Install dependencies
            self._install_dependencies()
            
            # Create profiles
            self._create_profiles()
            
            # Configure Conan
            self._configure_conan()
            
            logger.info("✅ Conan development environment setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    def _create_virtual_environment(self):
        """Create a virtual environment for Conan"""
        logger.info("🐍 Creating Python virtual environment...")
        
        if self.venv_dir.exists():
            shutil.rmtree(self.venv_dir)
        
        venv.create(self.venv_dir, with_pip=True)
        
        # Update Python executable path
        self.python_executable = self._get_python_executable()
        
        logger.info(f"✅ Virtual environment created: {self.venv_dir}")
    
    def _install_dependencies(self):
        """Install Python dependencies in the virtual environment"""
        logger.info("📦 Installing Python dependencies...")
        
        requirements = [
            "conan>=2.0.0",
            "pyyaml>=6.0",
            "requests>=2.28.0",
            "click>=8.0.0",
            "rich>=13.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "psutil>=5.9.0",  # For cross-platform process management
        ]
        
        for req in requirements:
            try:
                subprocess.run([
                    str(self.python_executable), "-m", "pip", "install", req
                ], check=True, capture_output=True)
                logger.info(f"✅ Installed: {req}")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install {req}: {e}")
                raise
    
    def _create_profiles(self):
        """Create Conan profiles for the current platform"""
        logger.info("📝 Creating Conan profiles...")
        
        # Platform-specific profiles
        platform_profiles = self._get_platform_profiles()
        
        for profile_name, profile in platform_profiles.items():
            profile_file = self.profiles_dir / f"{profile_name}.profile"
            self._write_profile_file(profile_file, profile)
            logger.info(f"📝 Created profile: {profile_name}")
    
    def _get_platform_profiles(self) -> Dict[str, ConanProfile]:
        """Get platform-specific profiles"""
        profiles = {}
        
        if self.platform == Platform.LINUX:
            profiles.update({
                "linux-gcc11": self.profiles.get("linux-gcc11"),
                "linux-clang15": self.profiles.get("linux-clang15"),
                "debug": self._create_debug_profile("linux-gcc11")
            })
        elif self.platform == Platform.WINDOWS:
            profiles.update({
                "windows-msvc2022": self.profiles.get("windows-msvc2022"),
                "debug": self._create_debug_profile("windows-msvc2022")
            })
        elif self.platform == Platform.MACOS:
            profiles.update({
                "macos-clang14": self.profiles.get("macos-clang14"),
                "debug": self._create_debug_profile("macos-clang14")
            })
        
        return {k: v for k, v in profiles.items() if v is not None}
    
    def _create_debug_profile(self, base_profile_name: str) -> ConanProfile:
        """Create a debug profile based on a base profile"""
        base_profile = self.profiles.get(base_profile_name)
        if not base_profile:
            return None
        
        debug_profile = ConanProfile(
            name="debug",
            os=base_profile.os,
            arch=base_profile.arch,
            compiler=base_profile.compiler,
            compiler_version=base_profile.compiler_version,
            compiler_libcxx=base_profile.compiler_libcxx,
            build_type="Debug",
            generator=base_profile.generator,
            extra_conf=base_profile.extra_conf.copy()
        )
        
        return debug_profile
    
    def _write_profile_file(self, profile_file: Path, profile: ConanProfile):
        """Write a Conan profile to file"""
        with open(profile_file, 'w') as f:
            f.write("[settings]\n")
            f.write(f"os={profile.os}\n")
            f.write(f"arch={profile.arch}\n")
            f.write(f"compiler={profile.compiler}\n")
            f.write(f"compiler.version={profile.compiler_version}\n")
            f.write(f"compiler.libcxx={profile.compiler_libcxx}\n")
            f.write(f"build_type={profile.build_type}\n")
            
            if profile.extra_conf:
                f.write("\n[conf]\n")
                for key, value in profile.extra_conf.items():
                    f.write(f"{key}={value}\n")
    
    def _configure_conan(self):
        """Configure Conan settings"""
        logger.info("⚙️ Configuring Conan...")
        
        # Get Conan home directory
        conan_exe = self._get_conan_executable()
        result = subprocess.run([str(conan_exe), "config", "home"], 
                              capture_output=True, text=True, check=True)
        conan_home = Path(result.stdout.strip())
        conan_profiles_dir = conan_home / "profiles"
        conan_profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy profiles to Conan's profile directory
        for profile_file in self.profiles_dir.glob("*.profile"):
            target_file = conan_profiles_dir / profile_file.name
            shutil.copy2(profile_file, target_file)
            logger.info(f"📝 Copied profile to Conan: {profile_file.name}")
        
        # Create Conan configuration
        conan_config = {
            "storage": {"path": str(self.cache_dir)},
            "remotes": {"conancenter": "https://center.conan.io"},
            "log": {"level": "info"},
            "tools": {
                "cmake.cmaketoolchain:generator": "Ninja",
                "system.package_manager:mode": "install"
            },
            "cache": {"no_locks": "False"}
        }
        
        # Platform-specific configuration
        if self.platform == Platform.WINDOWS:
            conan_config["tools"]["cmake.cmaketoolchain:generator"] = "Visual Studio 17 2022"
        elif self.platform == Platform.MACOS:
            conan_config["tools"]["cmake.cmaketoolchain:generator"] = "Xcode"
        
        # Write configuration
        config_file = self.conan_dir / "conan.conf"
        with open(config_file, 'w') as f:
            for section, settings in conan_config.items():
                f.write(f"[{section}]\n")
                for key, value in settings.items():
                    f.write(f"{key} = {value}\n")
                f.write("\n")
    
    def install(self, profile: str = None, verbose: bool = False, clean: bool = False) -> bool:
        """Install Conan dependencies"""
        try:
            if not profile:
                profile = self._get_default_profile()
            
            logger.info(f"🚀 Installing Conan dependencies...")
            logger.info(f"📋 Profile: {profile}")
            logger.info(f"🐍 Python: {self.python_executable}")
            
            # Validate profile
            if profile not in self.profiles:
                logger.error(f"❌ Profile not found: {profile}")
                logger.info(f"Available profiles: {', '.join(self.profiles.keys())}")
                return False
            
            # Clean if requested
            if clean:
                self._clean_build()
            
            # Run conan install
            conan_exe = self._get_conan_executable()
            profile_name = f"{profile}.profile" if not profile.endswith('.profile') else profile
            cmd = [
                str(conan_exe), "install", ".",
                "--profile", profile_name,
                "--build", "missing"
            ]
            
            if verbose:
                cmd.append("-v")
            
            logger.info(f"🔧 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=self.project_root, check=True)
            
            logger.info("✅ Installation complete!")
            logger.info("💡 Next step: Run 'conan-orchestrator build' to build the package")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Installation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def build(self, profile: str = None, verbose: bool = False, clean: bool = False, test: bool = False) -> bool:
        """Build Conan package"""
        try:
            if not profile:
                profile = self._get_default_profile()
            
            logger.info(f"🔨 Building Conan package...")
            logger.info(f"📋 Profile: {profile}")
            
            # Validate profile
            if profile not in self.profiles:
                logger.error(f"❌ Profile not found: {profile}")
                logger.info(f"Available profiles: {', '.join(self.profiles.keys())}")
                return False
            
            # Clean if requested
            if clean:
                self._clean_build()
            
            # Run conan build
            conan_exe = self._get_conan_executable()
            profile_name = f"{profile}.profile" if not profile.endswith('.profile') else profile
            cmd = [
                str(conan_exe), "build", ".",
                "--profile", profile_name
            ]
            
            if verbose:
                cmd.append("-v")
            
            logger.info(f"🔧 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=self.project_root, check=True)
            
            # Run tests if requested
            if test:
                self._run_tests(profile, verbose)
            
            logger.info("✅ Build complete!")
            logger.info("📁 Build artifacts: build/ and package/ directories")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Build failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def test(self, profile: str = None, verbose: bool = False) -> bool:
        """Run Conan tests"""
        try:
            if not profile:
                profile = self._get_default_profile()
            
            logger.info(f"🧪 Running Conan tests...")
            logger.info(f"📋 Profile: {profile}")
            
            return self._run_tests(profile, verbose)
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return False
    
    def _run_tests(self, profile: str, verbose: bool = False) -> bool:
        """Run Conan tests"""
        try:
            conan_exe = self._get_conan_executable()
            profile_name = f"{profile}.profile" if not profile.endswith('.profile') else profile
            cmd = [
                str(conan_exe), "test", "test_package",
                "openssl/3.5.0@user/channel",
                "--profile", profile_name
            ]
            
            if verbose:
                cmd.append("-v")
            
            logger.info(f"🔧 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=self.project_root, check=True)
            
            logger.info("✅ Tests completed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Tests failed: {e}")
            return False
    
    def _get_default_profile(self) -> str:
        """Get the default profile for the current platform"""
        if self.platform == Platform.LINUX:
            return "linux-gcc11"
        elif self.platform == Platform.WINDOWS:
            return "windows-msvc2022"
        elif self.platform == Platform.MACOS:
            return "macos-clang14"
        else:
            return "linux-gcc11"
    
    def _clean_build(self):
        """Clean previous build artifacts"""
        logger.info("🧹 Cleaning previous build...")
        
        try:
            # Remove Conan packages
            conan_exe = self._get_conan_executable()
            subprocess.run([
                str(conan_exe), "remove", "*", "--force"
            ], cwd=self.project_root, check=True, capture_output=True)
            
            # Remove build directories
            build_dirs = ["build", "package"]
            for build_dir in build_dirs:
                build_path = self.project_root / build_dir
                if build_path.exists():
                    shutil.rmtree(build_path)
                    
        except subprocess.CalledProcessError as e:
            logger.warning(f"Clean failed: {e}")
    
    def list_profiles(self):
        """List available profiles"""
        logger.info("📋 Available profiles:")
        for name, profile in self.profiles.items():
            logger.info(f"  {name}: {profile.os} {profile.compiler} {profile.compiler_version} ({profile.build_type})")
    
    def show_info(self):
        """Show environment information"""
        logger.info("🔍 Conan Orchestrator Environment Info:")
        logger.info(f"  Platform: {self.platform.value}")
        logger.info(f"  Python: {self.python_executable}")
        logger.info(f"  Project Root: {self.project_root}")
        logger.info(f"  Conan Dir: {self.conan_dir}")
        logger.info(f"  Virtual Env: {self.venv_dir}")
        logger.info(f"  Profiles: {len(self.profiles)} available")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Conan Orchestrator - Cross-platform Conan development tool")
    parser.add_argument("command", choices=["setup", "install", "build", "test", "list-profiles", "info"],
                       help="Command to execute")
    parser.add_argument("--profile", "-p", help="Conan profile to use")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--clean", "-c", action="store_true", help="Clean before operation")
    parser.add_argument("--test", "-t", action="store_true", help="Run tests after build")
    parser.add_argument("--force", "-f", action="store_true", help="Force setup (recreate environment)")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = ConanOrchestrator(args.project_root)
    
    # Execute command
    if args.command == "setup":
        success = orchestrator.setup_environment(force=args.force)
    elif args.command == "install":
        success = orchestrator.install(profile=args.profile, verbose=args.verbose, clean=args.clean)
    elif args.command == "build":
        success = orchestrator.build(profile=args.profile, verbose=args.verbose, clean=args.clean, test=args.test)
    elif args.command == "test":
        success = orchestrator.test(profile=args.profile, verbose=args.verbose)
    elif args.command == "list-profiles":
        orchestrator.list_profiles()
        success = True
    elif args.command == "info":
        orchestrator.show_info()
        success = True
    else:
        logger.error(f"Unknown command: {args.command}")
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()