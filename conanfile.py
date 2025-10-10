#!/usr/bin/env python3
"""
OpenSSL Conan Package Recipe - Minimal & Focused
Simplified Conan 2.x recipe for basic OpenSSL building
"""

from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps
from conan.tools.files import copy, load
from conan.errors import ConanInvalidConfiguration
import os
import re


class OpenSSLConan(ConanFile):
    name = "openssl"
    version = None  # Dynamically determined from VERSION.dat
    
    description = "OpenSSL is a robust, commercial-grade, full-featured toolkit for TLS and SSL protocols"
    homepage = "https://www.openssl.org"
    url = "https://github.com/openssl/openssl"
    license = "Apache-2.0"
    topics = ("ssl", "tls", "cryptography", "security")
    
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fips": [True, False],
        "enable_quic": [True, False],
        "no_asm": [True, False],
        "no_threads": [True, False],
        "openssldir": ["ANY"],
        "enable_unit_test": [True, False],
    }
    
    default_options = {
        "shared": True,
        "fPIC": True,
        "fips": False,
        "enable_quic": True,
        "no_asm": False,
        "no_threads": False,
        "openssldir": "/usr/local/ssl",
        "enable_unit_test": False,
    }
    
    def build_requirements(self):
        if self.settings.os == "Windows":
            self.tool_requires("nasm/2.15.05")
            self.tool_requires("strawberryperl/5.32.0.1")
        
    def requirements(self):
        # Keep minimal for basic functionality
        pass
        
    def set_version(self):
        """Get version from VERSION.dat"""
        version_file = os.path.join(self.recipe_folder, "VERSION.dat")
        if not os.path.exists(version_file):
            self.output.warning("VERSION.dat not found, using default version 3.0.0")
            self.version = "3.0.0"
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
                self.output.info(f"OpenSSL version: {self.version}")
            else:
                raise ConanInvalidConfiguration("Cannot parse VERSION.dat")
        except Exception as e:
            self.output.error(f"Failed to read VERSION.dat: {e}")
            raise
                
    def configure(self):
        if not self.options.shared:
            del self.options.fPIC
            
        # Essential validation
        if self.options.fips and self.options.no_asm:
            raise ConanInvalidConfiguration("FIPS mode requires assembly optimizations")
    
    def validate(self):
        if self.options.no_threads and self.options.enable_quic:
            raise ConanInvalidConfiguration("QUIC requires threading support")
            
    def export_sources(self):
        copy(self, "*", src=self.recipe_folder, dst=self.export_sources_folder)
        
    def layout(self):
        pass
        
    def generate(self):
        deps = AutotoolsDeps(self)
        deps.generate()
        
        tc = AutotoolsToolchain(self)
        tc.generate()
        
    def _get_configure_command(self):
        """Generate basic configure command"""
        args = ["./config"]
        
        if not os.path.exists("./config"):
            raise ConanInvalidConfiguration("OpenSSL config script not found")
        
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
        
        args.append(f"--openssldir={self.options.openssldir}")
        args.append(f"--prefix={self.package_folder}")
        
        if self.settings.build_type == "Debug":
            args.append("--debug")
        elif self.settings.build_type == "Release":
            args.append("--release")
            
        return args
        
    def build(self):
        """Basic build"""
        configure_args = self._get_configure_command()
        self.run(" ".join(configure_args))
        
        jobs = os.getenv("CONAN_CPU_COUNT", str(os.cpu_count() or 1))
        self.run(f"make -j{jobs}")
        
        if self.options.enable_unit_test:
            self.run("make test")
            
    def package(self):
        """Basic packaging"""
        self.run("make install_sw install_ssldirs")
        copy(self, "LICENSE.txt", src=".", dst=os.path.join(self.package_folder, "licenses"))
        
    def package_info(self):
        """Basic package info"""
        self.cpp_info.components["ssl"].libs = ["ssl"]
        self.cpp_info.components["ssl"].requires = ["crypto"]
        self.cpp_info.components["crypto"].libs = ["crypto"]
        
        if self.settings.os == "Linux":
            self.cpp_info.components["ssl"].system_libs.extend(["dl", "pthread"])
            self.cpp_info.components["crypto"].system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["ssl"].system_libs.extend(["ws2_32", "gdi32", "advapi32", "crypt32", "user32"])
            self.cpp_info.components["crypto"].system_libs.extend(["ws2_32", "gdi32", "advapi32", "crypt32", "user32"])