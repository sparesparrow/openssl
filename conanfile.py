#!/usr/bin/env python3
"""
OpenSSL Conan Package Recipe
Production-ready implementation for upstream integration
"""

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, save, load, get, replace_in_file
from conan.tools.cmake import CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.system import package_manager
from conan.tools.scm import Git
import os
import re
import hashlib
import json
import uuid
from pathlib import Path


class OpenSSLConan(ConanFile):
    name = "openssl"
    version = "4.0.0-dev"

    # Package metadata
    description = "OpenSSL FIPS 140-3 compliant cryptographic library"
    homepage = "https://www.openssl.org"
    url = "https://github.com/openssl/openssl"
    license = "Apache-2.0"
    topics = ("openssl", "crypto", "fips", "security", "ssl", "tls")

    # Package configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_fips": [True, False],
        "enable_tests": [True, False],
        "enable_docs": [True, False],
        "enable_examples": [True, False],
        "no_ssl3": [True, False],
        "no_tls1": [True, False],
        "no_tls1_1": [True, False],
        "no_deprecated": [True, False],
        "no_engine": [True, False],
        "no_asm": [True, False],
        "no_threads": [True, False],
        "enable_quic": [True, False],
        "enable_zlib": [True, False],
        "enable_zstd": [True, False],
        "enable_sctp": [True, False],
        "enable_ktls": [True, False],
        "enable_asan": [True, False],
        "enable_ubsan": [True, False],
        "enable_msan": [True, False],
        "enable_tsan": [True, False],
    }

    default_options = {
        "shared": True,
        "fPIC": True,
        "enable_fips": False,
        "enable_tests": False,
        "enable_docs": False,
        "enable_examples": False,
        "no_ssl3": True,
        "no_tls1": True,
        "no_tls1_1": True,
        "no_deprecated": False,
        "no_engine": True,
        "no_asm": False,
        "no_threads": False,
        "enable_quic": True,
        "enable_zlib": False,
        "enable_zstd": False,
        "enable_sctp": False,
        "enable_ktls": False,
        "enable_asan": False,
        "enable_ubsan": False,
        "enable_msan": False,
        "enable_tsan": False,
    }

    # Build requirements
    def build_requirements(self):
        if self.options.enable_tests:
            self.tool_requires("gtest/1.14.0")
        if self.options.enable_docs:
            self.tool_requires("doxygen/1.9.8")
        if self.options.enable_zlib:
            self.requires("zlib/1.3")
        if self.options.enable_zstd:
            self.requires("zstd/1.5.5")

    def requirements(self):
        """Add tool requirements for layered architecture"""
        # Add openssl-tools as tool_requires for build orchestration
        self.tool_requires("openssl-tools/1.0.0")

    def configure(self):
        """Configure package options"""
        # Static builds need fPIC
        if not self.options.shared:
            self.options.fPIC = True

    def validate(self):
        """Validate configuration"""
        # FIPS mode requires specific configurations
        if self.options.enable_fips:
            if self.options.shared:
                raise ConanInvalidConfiguration("FIPS mode requires static libraries")
            if self.options.no_deprecated:
                raise ConanInvalidConfiguration("FIPS mode requires deprecated APIs")
            if self.options.enable_asan or self.options.enable_ubsan or self.options.enable_msan or self.options.enable_tsan:
                raise ConanInvalidConfiguration("FIPS mode is incompatible with sanitizers")

    def export_sources(self):
        """Export source files"""
        # Export essential source files for OpenSSL build
        copy(self, "*.pm", src=".", dst=self.export_sources_folder)
        copy(self, "*.conf", src=".", dst=self.export_sources_folder)
        copy(self, "*.tmpl", src=".", dst=self.export_sources_folder)
        copy(self, "*.info", src=".", dst=self.export_sources_folder)
        copy(self, "*.num", src=".", dst=self.export_sources_folder)
        copy(self, "config*", src=".", dst=self.export_sources_folder)
        copy(self, "Configure*", src=".", dst=self.export_sources_folder)
        copy(self, "Makefile*", src=".", dst=self.export_sources_folder)
        copy(self, "VERSION*", src=".", dst=self.export_sources_folder)
        copy(self, "LICENSE*", src=".", dst=self.export_sources_folder)
        copy(self, "README*", src=".", dst=self.export_sources_folder)
        copy(self, "include/**", src=".", dst=self.export_sources_folder)
        copy(self, "crypto/**", src=".", dst=self.export_sources_folder)
        copy(self, "ssl/**", src=".", dst=self.export_sources_folder)
        copy(self, "apps/**", src=".", dst=self.export_sources_folder)
        copy(self, "test/**", src=".", dst=self.export_sources_folder)
        copy(self, "util/**", src=".", dst=self.export_sources_folder)
        copy(self, "engines/**", src=".", dst=self.export_sources_folder)
        copy(self, "providers/**", src=".", dst=self.export_sources_folder)
        copy(self, "fuzz/**", src=".", dst=self.export_sources_folder)
        copy(self, "doc/**", src=".", dst=self.export_sources_folder)
        copy(self, "*.py", src=".", dst=self.export_sources_folder)
        copy(self, "*.dat", src=".", dst=self.export_sources_folder)
        copy(self, "*.txt", src=".", dst=self.export_sources_folder)
        copy(self, "*.com", src=".", dst=self.export_sources_folder)
        copy(self, "*.in", src=".", dst=self.export_sources_folder)
        copy(self, "*.inc", src=".", dst=self.export_sources_folder)
        copy(self, "*.checksum", src=".", dst=self.export_sources_folder)
        copy(self, "*.c", src=".", dst=self.export_sources_folder)
        copy(self, "*.checksums", src=".", dst=self.export_sources_folder)
        copy(self, "*.sources", src=".", dst=self.export_sources_folder)
        copy(self, "*.h", src=".", dst=self.export_sources_folder)
        copy(self, "*.H", src=".", dst=self.export_sources_folder)
        copy(self, "*.asn1", src=".", dst=self.export_sources_folder)
        copy(self, "*.ec", src=".", dst=self.export_sources_folder)
        copy(self, "*.pl", src=".", dst=self.export_sources_folder)
        copy(self, "*.S", src=".", dst=self.export_sources_folder)
        copy(self, "*.asm", src=".", dst=self.export_sources_folder)
        copy(self, "*.m4", src=".", dst=self.export_sources_folder)
        copy(self, "*.pem", src=".", dst=self.export_sources_folder)
        copy(self, "*.der", src=".", dst=self.export_sources_folder)
        copy(self, "*.bin", src=".", dst=self.export_sources_folder)
        copy(self, "*.cnf", src=".", dst=self.export_sources_folder)
        copy(self, "*.pfx", src=".", dst=self.export_sources_folder)
        copy(self, "*.ors", src=".", dst=self.export_sources_folder)
        copy(self, "*.sh", src=".", dst=self.export_sources_folder)
        copy(self, "*.attr", src=".", dst=self.export_sources_folder)
        copy(self, "*.sct", src=".", dst=self.export_sources_folder)
        copy(self, "*.t", src=".", dst=self.export_sources_folder)
        copy(self, "*.crt", src=".", dst=self.export_sources_folder)
        copy(self, "*.key", src=".", dst=self.export_sources_folder)
        copy(self, "*.p12", src=".", dst=self.export_sources_folder)
        copy(self, "*.cms", src=".", dst=self.export_sources_folder)
        copy(self, "*.0", src=".", dst=self.export_sources_folder)
        copy(self, "*.ascii", src=".", dst=self.export_sources_folder)
        copy(self, "*.utf8", src=".", dst=self.export_sources_folder)
        copy(self, "*.pvk", src=".", dst=self.export_sources_folder)
        copy(self, "*.msb", src=".", dst=self.export_sources_folder)
        copy(self, "*.csr", src=".", dst=self.export_sources_folder)
        copy(self, "*.expected", src=".", dst=self.export_sources_folder)
        copy(self, "*.noncnf", src=".", dst=self.export_sources_folder)
        copy(self, "*.expected2", src=".", dst=self.export_sources_folder)
        copy(self, "*.expected1", src=".", dst=self.export_sources_folder)
        copy(self, "*.bak", src=".", dst=self.export_sources_folder)
        copy(self, "*.tsq", src=".", dst=self.export_sources_folder)
        copy(self, "*.tsr", src=".", dst=self.export_sources_folder)
        copy(self, "*.csv", src=".", dst=self.export_sources_folder)
        copy(self, "*.pkcs7", src=".", dst=self.export_sources_folder)
        copy(self, "*.out", src=".", dst=self.export_sources_folder)
        copy(self, "*.text", src=".", dst=self.export_sources_folder)
        copy(self, "*.tlssct", src=".", dst=self.export_sources_folder)
        copy(self, "*.eml", src=".", dst=self.export_sources_folder)
        copy(self, "*.Configure", src=".", dst=self.export_sources_folder)
        copy(self, "*.srl", src=".", dst=self.export_sources_folder)
        copy(self, "*.config", src=".", dst=self.export_sources_folder)
        copy(self, "*.syms", src=".", dst=self.export_sources_folder)
        copy(self, "*.rb", src=".", dst=self.export_sources_folder)
        copy(self, "*.pro", src=".", dst=self.export_sources_folder)
        copy(self, "*.sed", src=".", dst=self.export_sources_folder)
        copy(self, "*.json", src=".", dst=self.export_sources_folder)
        copy(self, "*.el", src=".", dst=self.export_sources_folder)
        copy(self, "*.pod", src=".", dst=self.export_sources_folder)
        copy(self, "*.png", src=".", dst=self.export_sources_folder)
        copy(self, "*.dot", src=".", dst=self.export_sources_folder)
        copy(self, "*.ods", src=".", dst=self.export_sources_folder)
        copy(self, "*.svg", src=".", dst=self.export_sources_folder)
        copy(self, "*.plantuml", src=".", dst=self.export_sources_folder)
        copy(self, "*.odg", src=".", dst=self.export_sources_folder)
        copy(self, "*.def", src=".", dst=self.export_sources_folder)

    def set_version(self):
        """Parse version from VERSION.dat file"""
        try:
            version_file = os.path.join(self.recipe_folder, "VERSION.dat")
            if os.path.exists(version_file):
                version_content = load(self, version_file)
                # Parse version from VERSION.dat format: MAJOR=4, MINOR=0, PATCH=0, PRE_RELEASE_TAG=dev
                major = re.search(r'MAJOR=(\d+)', version_content).group(1)
                minor = re.search(r'MINOR=(\d+)', version_content).group(1)
                patch = re.search(r'PATCH=(\d+)', version_content).group(1)
                pre_release = re.search(r'PRE_RELEASE_TAG=([^\n\r]*)', version_content).group(1)
                
                if pre_release and pre_release.strip():
                    self.version = f"{major}.{minor}.{patch}-{pre_release.strip()}"
                else:
                    self.version = f"{major}.{minor}.{patch}"
                
                self.output.info(f"Parsed version from VERSION.dat: {self.version}")
            else:
                self.output.warning("VERSION.dat not found, using default version")
        except Exception as e:
            self.output.warning(f"Failed to parse version from VERSION.dat: {e}")

    def source(self):
        """Get source code and configure for cloudsmth remote"""
        # Source is already available in the repository
        self.output.info("Source code available in repository")
        
        # Configure for cloudsmth remote caching
        self._configure_source_for_cloudsmth()

    def _get_configure_args(self):
        """Build configure arguments based on options"""
        args = []
        
        # Platform-specific configuration
        if self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                args.append("linux-x86_64")
            elif self.settings.arch == "armv8":
                args.append("linux-aarch64")
            else:
                args.append("linux-generic64")
        elif self.settings.os == "Windows":
            if self.settings.compiler == "msvc":
                args.append("VC-WIN64A" if self.settings.arch == "x86_64" else "VC-WIN32")
            else:
                args.append("mingw64" if self.settings.arch == "x86_64" else "mingw")
        elif self.settings.os == "Macos":
            if self.settings.arch == "armv8":
                args.append("darwin64-arm64-cc")
            else:
                args.append("darwin64-x86_64-cc")
        
        # Shared/static libraries
        if not self.options.shared:
            args.append("no-shared")
        
        # Position independent code
        if self.options.fPIC:
            args.append("-fPIC")
        
        # FIPS mode
        if self.options.enable_fips:
            args.append("enable-fips")
        
        # SSL/TLS protocol options
        if self.options.no_ssl3:
            args.append("no-ssl3")
        if self.options.no_tls1:
            args.append("no-tls1")
        if self.options.no_tls1_1:
            args.append("no-tls1_1")
        
        # Feature options
        if self.options.no_deprecated:
            args.append("no-deprecated")
        if self.options.no_engine:
            args.append("no-engine")
        if self.options.no_asm:
            args.append("no-asm")
        if self.options.no_threads:
            args.append("no-threads")
        if self.options.enable_quic:
            args.append("enable-quic")
        if self.options.enable_zlib:
            args.append("zlib")
        if self.options.enable_zstd:
            args.append("zstd")
        if self.options.enable_sctp:
            args.append("sctp")
        if self.options.enable_ktls:
            args.append("enable-ktls")
        
        # Sanitizers
        if self.options.enable_asan:
            args.append("enable-asan")
        if self.options.enable_ubsan:
            args.append("enable-ubsan")
        if self.options.enable_msan:
            args.append("enable-msan")
        if self.options.enable_tsan:
            args.append("enable-tsan")
        
        # Build type specific options
        if self.settings.build_type == "Debug":
            args.append("--debug")
        
        return args

    def build(self):
        """Build OpenSSL using traditional Configure/Make"""
        self.output.info("Building OpenSSL using traditional Configure/Make build system")
        
        # Configure OpenSSL
        configure_args = self._get_configure_args()
        configure_cmd = f"./Configure {' '.join(configure_args)} --prefix=/usr/local/ssl"
        
        self.output.info(f"Configure command: {configure_cmd}")
        self.run(configure_cmd, cwd=self.source_folder)
        
        # Build OpenSSL
        jobs = os.getenv("CONAN_CPU_COUNT", "1")
        self.run(f"make -j{jobs}", cwd=self.source_folder)
        
        # Run tests if enabled
        if self.options.enable_tests:
            self.output.info("Running OpenSSL tests")
            self.run("make test", cwd=self.source_folder)

    def package(self):
        """Package OpenSSL"""
        # Install OpenSSL to package folder
        self.run("make install_sw install_ssldirs DESTDIR=" + self.package_folder, cwd=self.source_folder)
        
        # Copy license
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        
        # Generate SBOM
        self._generate_sbom()
        
        # Configure for cloudsmth remote caching
        self._configure_package_for_cloudsmth()
        
        self.output.info("Packaging OpenSSL completed")

    def _generate_sbom(self):
        """Generate Software Bill of Materials"""
        try:
            sbom_data = {
                "bomFormat": "CycloneDX",
                "specVersion": "1.4",
                "version": 1,
                "metadata": {
                    "timestamp": str(uuid.uuid4()),
                    "tools": [
                        {
                            "vendor": "OpenSSL",
                            "name": "Conan Package",
                            "version": self.version
                        }
                    ],
                    "component": {
                        "type": "library",
                        "name": self.name,
                        "version": self.version,
                        "description": self.description,
                        "licenses": [{"id": self.license}],
                        "purl": f"pkg:conan/{self.name}@{self.version}",
                        "properties": [
                            {"name": "build_type", "value": str(self.settings.build_type)},
                            {"name": "shared", "value": str(self.options.shared)},
                            {"name": "enable_fips", "value": str(self.options.enable_fips)},
                            {"name": "os", "value": str(self.settings.os)},
                            {"name": "arch", "value": str(self.settings.arch)},
                            {"name": "compiler", "value": str(self.settings.compiler)},
                        ]
                    }
                },
                "components": [
                    {
                        "type": "library",
                        "name": self.name,
                        "version": self.version,
                        "description": self.description,
                        "licenses": [{"id": self.license}],
                        "purl": f"pkg:conan/{self.name}@{self.version}"
                    }
                ]
            }
            
            sbom_path = os.path.join(self.package_folder, "sbom.json")
            save(self, sbom_path, json.dumps(sbom_data, indent=2))
            self.output.info(f"SBOM generated: {sbom_path}")
            
        except Exception as e:
            self.output.warn(f"Failed to generate SBOM: {e}")

    def _configure_source_for_cloudsmth(self):
        """Configure source for cloudsmth remote caching"""
        try:
            # Set up environment for cloudsmth remote
            self.output.info("Configuring source for cloudsmth remote caching")
            
            # Set environment variables for cloudsmth remote
            os.environ["CONAN_REMOTES"] = "cloudsmth,conancenter"
            os.environ["CONAN_CACHE_ENABLED"] = "1"
            
            self.output.info("Source configured for cloudsmth remote")
            
        except Exception as e:
            self.output.warning(f"Failed to configure source for cloudsmth: {e}")

    def _configure_package_for_cloudsmth(self):
        """Configure package for cloudsmth remote caching"""
        try:
            # Create package metadata for cloudsmth caching
            package_metadata = {
                "remote": "cloudsmth",
                "cache_enabled": True,
                "build_type": str(self.settings.build_type),
                "arch": str(self.settings.arch),
                "os": str(self.settings.os),
                "compiler": str(self.settings.compiler),
                "version": self.version,
                "shared": self.options.shared,
                "fips_enabled": self.options.enable_fips,
                "timestamp": str(uuid.uuid4())
            }
            
            # Save metadata for cloudsmth remote
            metadata_path = os.path.join(self.package_folder, "cloudsmth_metadata.json")
            save(self, metadata_path, json.dumps(package_metadata, indent=2))
            
            self.output.info("Package configured for cloudsmth remote caching")
            
        except Exception as e:
            self.output.warning(f"Failed to configure package for cloudsmth: {e}")

    def package_info(self):
        """Package info for OpenSSL"""
        # Libraries
        self.cpp_info.libs = ["ssl", "crypto"]

        # Paths
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        
        # System libraries
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "gdi32", "advapi32", "crypt32", "user32"])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.append("Security")
        
        # Environment variables
        self.runenv_info.define("OPENSSL_ROOT_DIR", self.package_folder)
        self.runenv_info.define("OPENSSL_CONF", os.path.join(self.package_folder, "ssl", "openssl.cnf"))
        
        # CMake variables
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")
        self.cpp_info.set_property("cmake_target_name", "OpenSSL::SSL")
        self.cpp_info.set_property("cmake_target_aliases", ["OpenSSL::Crypto"])
        
        # PKG_CONFIG
        self.cpp_info.set_property("pkg_config_name", "openssl")
        
        # Version info
        self.cpp_info.set_property("version", self.version)
        
        # FIPS mode indicator
        if self.options.enable_fips:
            self.cpp_info.defines.append("OPENSSL_FIPS")
            self.runenv_info.define("OPENSSL_FIPS", "1")