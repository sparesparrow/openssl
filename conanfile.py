#!/usr/bin/env python3
"""
OpenSSL Conan Package Recipe
Modern dependency management for OpenSSL CI/CD pipeline with enhanced security
"""

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, save, load
from conan.tools.scm import Git
from conan.tools.system import package_manager
from conan.errors import ConanInvalidConfiguration
import os
import re
import hashlib
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
    
    # Package configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fips": [True, False],
        "no_asm": [True, False],
        "no_threads": [True, False],
        "no_zlib": [True, False],
        "no_egd": [True, False],
        "386": [True, False],
        "no_sse2": [True, False],
        "no_bf": [True, False],
        "no_cast": [True, False],
        "no_des": [True, False],
        "no_dh": [True, False],
        "no_dsa": [True, False],
        "no_hmac": [True, False],
        "no_md2": [True, False],
        "no_md4": [True, False],
        "no_md5": [True, False],
        "no_mdc2": [True, False],
        "no_rc2": [True, False],
        "no_rc4": [True, False],
        "no_rc5": [True, False],
        "no_rsa": [True, False],
        "no_sha": [True, False],
        "openssldir": "ANY",
        "cafile": "ANY",
        "capath": "ANY",
        "no_pinshared": [True, False],
        "no_stdio": [True, False],
        "enable_weak_ssl_ciphers": [True, False],
        "enable_ssl3": [True, False],
        "enable_ssl3_method": [True, False],
        "enable_trace": [True, False],
        "enable_unit_test": [True, False],
        "enable_ubsan": [True, False],
        "enable_asan": [True, False],
        "enable_msan": [True, False],
        "enable_tsan": [True, False],
        "enable_fuzzer_afl": [True, False],
        "enable_fuzzer_libfuzzer": [True, False],
        "enable_external_tests": [True, False],
        "enable_buildtest_c++": [True, False],
        "enable_crypto_mdebug": [True, False],
        "enable_crypto_mdebug_backtrace": [True, False],
        "enable_lms": [True, False],
        "enable_quic": [True, False],
        "enable_h3demo": [True, False],
        "enable_demos": [True, False],
    }
    
    default_options = {
        "shared": True,
        "fips": False,
        "no_asm": False,
        "no_threads": False,
        "no_zlib": False,
        "no_egd": True,
        "386": False,
        "no_sse2": False,
        "no_bf": False,
        "no_cast": False,
        "no_des": False,
        "no_dh": False,
        "no_dsa": False,
        "no_hmac": False,
        "no_md2": True,
        "no_md4": False,
        "no_md5": False,
        "no_mdc2": False,
        "no_rc2": False,
        "no_rc4": False,
        "no_rc5": True,
        "no_rsa": False,
        "no_sha": False,
        "openssldir": "",
        "cafile": "",
        "capath": "",
        "no_pinshared": False,
        "no_stdio": False,
        "enable_weak_ssl_ciphers": False,
        "enable_ssl3": False,
        "enable_ssl3_method": False,
        "enable_trace": False,
        "enable_unit_test": False,
        "enable_ubsan": False,
        "enable_asan": False,
        "enable_msan": False,
        "enable_tsan": False,
        "enable_fuzzer_afl": False,
        "enable_fuzzer_libfuzzer": False,
        "enable_external_tests": False,
        "enable_buildtest_c++": False,
        "enable_crypto_mdebug": False,
        "enable_crypto_mdebug_backtrace": False,
        "enable_lms": False,
        "enable_quic": True,
        "enable_h3demo": False,
        "enable_demos": False,
    }
    
    # Build requirements
    def build_requirements(self):
        self.tool_requires("perl/5.34.0")
        if self.settings.os == "Windows":
            self.tool_requires("nasm/2.15.05")
            self.tool_requires("strawberryperl/5.32.0.1")
        
    # Runtime requirements  
    def requirements(self):
        if not self.options.no_zlib:
            self.requires("zlib/1.3.1")
            
    def system_requirements(self):
        # System package requirements for different platforms
        package_manager.Apt(self).install(["build-essential", "perl"])
        package_manager.Yum(self).install(["gcc", "gcc-c++", "make", "perl"])
        package_manager.PacMan(self).install(["base-devel", "perl"])
        package_manager.Zypper(self).install(["gcc", "gcc-c++", "make", "perl"])
        
    def set_version(self):
        """Dynamically determine version from VERSION.dat"""
        version_file = os.path.join(self.recipe_folder, "VERSION.dat")
        if not os.path.exists(version_file):
            # Fallback for testing or if VERSION.dat is missing
            self.output.warning("VERSION.dat not found, using default version 3.5.0")
            self.version = "3.5.0"
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
        """Configure and validate build options"""
        # Configure build options based on settings
        if self.settings.build_type == "Debug":
            self.options.enable_crypto_mdebug = True
            
        # Security-focused builds
        if self.options.fips:
            self.options.enable_unit_test = True
            
        # Performance builds  
        if self.settings.build_type == "Release" and self.settings.arch in ["x86_64", "armv8"]:
            self.options.no_asm = False
    
    def validate(self):
        """Validate configuration options for conflicts"""
        # Check for conflicting options
        if self.options.fips and self.options.no_asm:
            raise ConanInvalidConfiguration(
                "FIPS mode requires assembly optimizations. "
                "Cannot use fips=True with no_asm=True. "
                "Set no_asm=False or disable FIPS."
            )
        
        if self.options.fips and self.settings.build_type == "Debug":
            self.output.warning(
                "FIPS validation may behave differently in Debug builds. "
                "Consider using Release build_type for production FIPS deployments."
            )
        
        # Sanitizers are mutually exclusive
        sanitizers = [
            self.options.enable_asan,
            self.options.enable_msan,
            self.options.enable_tsan
        ]
        if sum(sanitizers) > 1:
            raise ConanInvalidConfiguration(
                "Only one sanitizer can be enabled at a time. "
                "Choose either ASAN, MSAN, or TSAN, not multiple."
            )
        
        # Sanitizers don't work well with optimization
        if any(sanitizers) and self.settings.build_type == "Release":
            self.output.warning(
                "Sanitizers work best with Debug builds. "
                "Consider using build_type=Debug for sanitizer testing."
            )
        
        # Check for no_threads with QUIC (QUIC needs threading)
        if self.options.no_threads and self.options.enable_quic:
            raise ConanInvalidConfiguration(
                "QUIC protocol requires threading support. "
                "Cannot use no_threads=True with enable_quic=True."
            )
            
    def export_sources(self):
        # Export all source files
        copy(self, "*", src=self.recipe_folder, dst=self.export_sources_folder)
        
    def layout(self):
        # Use basic layout for custom build system
        # OpenSSL builds in-tree, so we don't separate source and build
        pass
        
    def generate(self):
        # Generate build environment
        deps = CMakeDeps(self)
        deps.generate()
        
        tc = CMakeToolchain(self)
        tc.generate()
        
    def _get_configure_command(self):
        """Generate OpenSSL configure command based on options"""
        args = ["./config", "--banner=Configured"]
        
        # Basic options
        if not self.options.shared:
            args.append("no-shared")
            
        if self.options.fips:
            args.append("enable-fips")
            
        if self.options.no_asm:
            args.append("no-asm")
            
        if self.options.no_threads:
            args.append("no-threads")
            
        # Crypto options
        crypto_options = [
            "bf", "cast", "des", "dh", "dsa", "hmac", "md2", "md4", "md5", 
            "mdc2", "rc2", "rc4", "rc5", "rsa", "sha"
        ]
        
        for option in crypto_options:
            if getattr(self.options, f"no_{option}"):
                args.append(f"no-{option}")
                
        # Enable options
        enable_options = [
            "weak_ssl_ciphers", "ssl3", "ssl3_method", "trace", "unit_test",
            "ubsan", "asan", "msan", "tsan", "fuzzer_afl", "fuzzer_libfuzzer",
            "external_tests", "buildtest_c++", "crypto_mdebug", 
            "crypto_mdebug_backtrace", "lms", "quic", "h3demo", "demos"
        ]
        
        for option in enable_options:
            if getattr(self.options, f"enable_{option}"):
                args.append(f"enable-{option.replace('_', '-')}")
                
        # Directories
        if self.options.openssldir:
            args.append(f"--openssldir={self.options.openssldir}")
        else:
            args.append(f"--openssldir={os.path.join(self.package_folder, 'ssl')}")
            
        args.append(f"--prefix={self.package_folder}")
        
        # Compiler flags
        if self.settings.build_type == "Debug":
            args.append("--debug")
        elif self.settings.build_type == "Release":
            args.append("--release")
            
        # Add strict warnings for CI builds
        if os.getenv("OSSL_RUN_CI_TESTS"):
            args.append("--strict-warnings")
            
        return args
        
    def build(self):
        # Configure OpenSSL
        configure_args = self._get_configure_command()
        self.run(" ".join(configure_args))
        
        # Build
        jobs = os.getenv("CONAN_CPU_COUNT", "1")
        self.run(f"make -j{jobs}")
        
        # Run tests if enabled
        if self.options.enable_unit_test or os.getenv("OSSL_RUN_CI_TESTS"):
            self.run("make test")
            
    def package(self):
        # Install OpenSSL
        self.run("make install_sw install_ssldirs")
        
        # Copy license
        copy(self, "LICENSE.txt", src=".", dst=os.path.join(self.package_folder, "licenses"))
        
        # Generate SBOM (Software Bill of Materials)
        self._generate_sbom()
        
    def _generate_sbom(self):
        """Generate Software Bill of Materials for supply chain security"""
        sbom_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "metadata": {
                "component": {
                    "type": "library",
                    "name": self.name,
                    "version": str(self.version),
                    "licenses": [{"license": {"id": "Apache-2.0"}}]
                }
            },
            "components": []
        }
        
        # Add dependencies to SBOM
        for dep in self.deps_cpp_info.deps:
            component = {
                "type": "library", 
                "name": dep,
                "version": str(self.deps_cpp_info[dep].version),
                "scope": "required"
            }
            sbom_data["components"].append(component)
            
        import json
        sbom_path = os.path.join(self.package_folder, "sbom.json")
        save(self, sbom_path, json.dumps(sbom_data, indent=2))
        
    def package_info(self):
        # Set package information
        self.cpp_info.libs = ["ssl", "crypto"]
        
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "gdi32", "advapi32", "crypt32", "user32"])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.append("Security")
            
        # Set binary paths
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        
        # Environment variables
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        
        # OpenSSL specific configurations
        if self.options.openssldir:
            self.env_info.OPENSSL_CONF = os.path.join(str(self.options.openssldir), "openssl.cnf")
        else:
            self.env_info.OPENSSL_CONF = os.path.join(self.package_folder, "ssl", "openssl.cnf")
            
    def package_id(self):
        # Customize package ID for better caching
        del self.info.options.openssldir
        del self.info.options.cafile  
        del self.info.options.capath
        
        # Test-only options don't affect package ID
        del self.info.options.enable_unit_test
        del self.info.options.enable_external_tests