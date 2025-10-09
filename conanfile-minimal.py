#!/usr/bin/env python3
"""
OpenSSL Conan Package Recipe - Minimal Version
Simplified Conan 2.x recipe focused on core OpenSSL build functionality
Complex orchestration handled by openssl-tools repository
"""

from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.tools.files import copy, save, load, chdir
from conan.tools.scm import Git
from conan.tools.system import package_manager
from conan.errors import ConanInvalidConfiguration
import os
import re
import json


class OpenSSLConan(ConanFile):
    name = "openssl"
    version = None  # Dynamically determined from VERSION.dat
    
    # Package metadata
    description = "OpenSSL is a robust, commercial-grade, full-featured toolkit for TLS and SSL protocols"
    homepage = "https://www.openssl.org"
    url = "https://github.com/openssl/openssl"
    license = "Apache-2.0"
    topics = ("ssl", "tls", "cryptography", "security")
    
    # Package configuration - simplified core options only
    settings = "os", "compiler", "build_type", "arch"
    options = {
        # Core build options
        "shared": [True, False],
        "fPIC": [True, False],
        
        # Security & Compliance (essential)
        "fips": [True, False],
        "no_deprecated": [True, False],
        
        # Essential features
        "enable_quic": [True, False],
        "no_asm": [True, False],
        "no_threads": [True, False],
        
        # Essential directories
        "openssldir": ["ANY"],
        "cafile": ["ANY"], 
        "capath": ["ANY"],
        
        # Build control
        "enable_unit_test": [True, False],
    }
    
    default_options = {
        "shared": True,
        "fPIC": True,
        "fips": False,
        "no_deprecated": False,
        "enable_quic": True,
        "no_asm": False,
        "no_threads": False,
        "openssldir": "/usr/local/ssl",
        "cafile": "",
        "capath": "",
        "enable_unit_test": False,
    }
    
    def build_requirements(self):
        """Minimal build requirements"""
        if self.settings.os == "Windows":
            self.tool_requires("nasm/2.15.05")
            self.tool_requires("strawberryperl/5.32.0.1")
        
    def requirements(self):
        """Minimal runtime requirements"""
        # Only essential dependencies - complex dependency management in openssl-tools
        pass
        
    def set_version(self):
        """Dynamically determine version from VERSION.dat"""
        version_file = os.path.join(self.recipe_folder, "VERSION.dat")
        if not os.path.exists(version_file):
            self.output.warning("VERSION.dat not found, using default version 4.0.0")
            self.version = "4.0.0"
            return
            
        try:
            content = load(self, version_file)
            version_match = re.search(r'MAJOR=(\d+)', content)
            minor_match = re.search(r'MINOR=(\d+)', content)  
            patch_match = re.search(r'PATCH=(\d+)', content)
            
            if version_match and minor_match and patch_match:
                major = version_match.group(1)
                minor = minor_match.group(1)
                patch = patch_match.group(1)
                self.version = f"{major}.{minor}.{patch}"
                self.output.info(f"Detected OpenSSL version: {self.version}")
            else:
                raise ConanInvalidConfiguration("VERSION.dat exists but couldn't parse version numbers")
        except Exception as e:
            self.output.error(f"Failed to read VERSION.dat: {e}")
            raise
                
    def configure(self):
        """Basic configuration - complex logic handled by openssl-tools"""
        if not self.options.shared:
            del self.options.fPIC
            
        # Basic FIPS validation
        if self.options.fips and self.options.no_asm:
            raise ConanInvalidConfiguration(
                "FIPS mode requires assembly optimizations. "
                "Cannot use fips=True with no_asm=True."
            )
    
    def validate(self):
        """Essential validation only - comprehensive validation in openssl-tools"""
        # Only critical validations that prevent builds
        if self.options.fips and self.options.no_asm:
            raise ConanInvalidConfiguration("FIPS mode requires assembly optimizations")
        
        if self.options.no_threads and self.options.enable_quic:
            raise ConanInvalidConfiguration("QUIC protocol requires threading support")
            
    def export_sources(self):
        """Export source tree"""
        copy(self, "*", src=self.recipe_folder, dst=self.export_sources_folder)
        
    def layout(self):
        """Basic layout for OpenSSL's in-tree build system"""
        pass
        
    def generate(self):
        """Generate basic toolchain"""
        deps = AutotoolsDeps(self)
        deps.generate()
        
        tc = AutotoolsToolchain(self)
        tc.generate()
        
    def _get_configure_command(self):
        """Generate basic OpenSSL configure command"""
        args = ["./config", "--banner=Configured"]
        
        if not os.path.exists("./config"):
            raise ConanInvalidConfiguration("OpenSSL config script not found")
        
        # Basic options only
        if not self.options.shared:
            args.append("no-shared")
            
        if self.options.fips:
            args.append("enable-fips")
            
        if self.options.no_asm:
            args.append("no-asm")
            
        if self.options.no_threads:
            args.append("no-threads")
            
        if self.options.enable_quic:
            args.append("enable-quic")
            
        if self.options.no_deprecated:
            args.append("no-deprecated")
        
        # Directories
        if self.options.openssldir:
            args.append(f"--openssldir={self.options.openssldir}")
        else:
            args.append(f"--openssldir={os.path.join(self.package_folder, 'ssl')}")
            
        args.append(f"--prefix={self.package_folder}")
        
        # Build type
        if self.settings.build_type == "Debug":
            args.append("--debug")
        elif self.settings.build_type == "Release":
            args.append("--release")
            
        self.output.info(f"Configure command: {' '.join(args)}")
        return args
        
    def build(self):
        """Basic build - complex orchestration handled by openssl-tools"""
        # Configure OpenSSL
        configure_args = self._get_configure_command()
        self.run(" ".join(configure_args))
        
        # Build
        jobs = os.getenv("CONAN_CPU_COUNT", "1")
        self.run(f"make -j{jobs}")
        
        # Run tests if enabled
        if self.options.enable_unit_test and not self._should_skip_tests():
            self.run("make test")
            
    def _should_skip_tests(self):
        """Check if tests should be skipped"""
        return os.getenv("CONAN_SKIP_TESTS", "false").lower() == "true"
            
    def package(self):
        """Basic packaging"""
        self.run("make install_sw install_ssldirs")
        copy(self, "LICENSE.txt", src=".", dst=os.path.join(self.package_folder, "licenses"))
        
    def package_info(self):
        """Basic package information"""
        # Separate components for proper dependency resolution
        self.cpp_info.components["ssl"].libs = ["ssl"]
        self.cpp_info.components["ssl"].requires = ["crypto"]
        self.cpp_info.components["crypto"].libs = ["crypto"]
        
        # Platform-specific system libraries
        if self.settings.os == "Linux":
            self.cpp_info.components["ssl"].system_libs.extend(["dl", "pthread"])
            self.cpp_info.components["crypto"].system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["ssl"].system_libs.extend(["ws2_32", "gdi32", "advapi32", "crypt32", "user32"])
            self.cpp_info.components["crypto"].system_libs.extend(["ws2_32", "gdi32", "advapi32", "crypt32", "user32"])
        elif self.settings.os == "Macos":
            self.cpp_info.components["ssl"].frameworks.append("Security")
            self.cpp_info.components["crypto"].frameworks.append("Security")
            
        # Set paths
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        
        # Environment variables
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        
        if self.options.openssldir:
            self.env_info.OPENSSL_CONF = os.path.join(str(self.options.openssldir), "openssl.cnf")
        else:
            self.env_info.OPENSSL_CONF = os.path.join(self.package_folder, "ssl", "openssl.cnf")
            
    def package_id(self):
        """Optimized package ID for caching"""
        # Runtime path options don't affect binary compatibility
        del self.info.options.openssldir
        del self.info.options.cafile  
        del self.info.options.capath
        
        # Test options don't affect package ID
        del self.info.options.enable_unit_test
        
        # FIPS builds must have separate cache key
        if self.info.options.fips:
            self.info.options.fips = "fips_enabled"
        else:
            self.info.options.fips = "fips_disabled"