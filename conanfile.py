#!/usr/bin/env python3
"""
OpenSSL FIPS Conan Package Recipe
Based on ngapy-dev patterns for C development with FIPS compliance
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
import uuid
from pathlib import Path


class OpenSSLConan(ConanFile):
    name = "openssl"
    version = "3.3.0"

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
    }

    default_options = {
        "shared": True,
        "fPIC": True,
        "enable_fips": True,
        "enable_tests": True,
        "enable_docs": False,
        "enable_examples": False,
        "no_ssl3": True,
        "no_tls1": True,
        "no_tls1_1": True,
        "no_deprecated": False,
        "no_engine": True,
    }

    # Build requirements
    def build_requirements(self):
        if self.options.enable_tests:
            self.tool_requires("gtest/1.14.0")
        if self.options.enable_docs:
            self.tool_requires("doxygen/1.9.8")

    # Runtime requirements
    def requirements(self):
        if self.options.enable_fips:
            self.requires("openssl-fips-data/140-3.1")

    def system_requirements(self):
        """System requirements for OpenSSL build"""
        package_manager.Apt(self).install([
            "build-essential", "cmake", "git", "perl", "libperl-dev"
        ])
        package_manager.Yum(self).install([
            "gcc", "gcc-c++", "make", "cmake", "git", "perl", "perl-devel"
        ])
        package_manager.PacMan(self).install([
            "base-devel", "cmake", "git", "perl"
        ])
        package_manager.Zypper(self).install([
            "gcc", "gcc-c++", "make", "cmake", "git", "perl", "perl-devel"
        ])

    def set_version(self):
        """Set version from git tags or VERSION.dat"""
        try:
            git = Git(self)
            version = git.run("describe --tags --always --dirty")
            if version:
                version = version.strip().replace("v", "")
                self.version = version
            else:
                # Fallback to VERSION.dat
                version_file = os.path.join(self.source_folder, "VERSION.dat")
                if os.path.exists(version_file):
                    with open(version_file, 'r') as f:
                        version_data = f.read().strip()
                        # Parse VERSION.dat format
                        self.version = version_data.split()[0]
        except:
            self.version = "3.3.0"

    def configure(self):
        """Configure package options"""
        if self.options.enable_fips and not self.options.no_deprecated:
            self.output.warn("FIPS mode enabled with deprecated algorithms - consider setting no_deprecated=True")

        # Static builds need fPIC
        if not self.options.shared:
            self.options.fPIC = True

    def validate(self):
        """Validate configuration"""
        if self.options.enable_fips and self.settings.compiler == "gcc":
            if self.settings.compiler.version < "7":
                raise ConanInvalidConfiguration("FIPS mode requires GCC 7+")

        if self.options.enable_fips and self.options.no_deprecated:
            self.output.info("FIPS mode with no deprecated algorithms - maximum security")

    def source(self):
        """Get source code and fuzz corpora"""
        git = Git(self)
        # Clone fuzz corpora from separate repo
        git.clone(url="https://github.com/sparesparrow/fuzz-corpora.git", 
                  target="fuzz/corpora")

    def export_sources(self):
        """Export source files"""
        copy(self, "*", src=self.source_folder, dst=self.export_sources_folder)

    def layout(self):
        """Define build layout"""
        cmake_layout(self)

    def generate(self):
        """Generate build configuration"""
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["OPENSSL_FIPS"] = self.options.enable_fips
        tc.variables["ENABLE_TESTS"] = self.options.enable_tests
        tc.variables["ENABLE_EXAMPLES"] = self.options.enable_examples
        tc.variables["ENABLE_DOCS"] = self.options.enable_docs
        tc.variables["OPENSSL_NO_SSL3"] = self.options.no_ssl3
        tc.variables["OPENSSL_NO_TLS1"] = self.options.no_tls1
        tc.variables["OPENSSL_NO_TLS1_1"] = self.options.no_tls1_1
        tc.variables["OPENSSL_NO_DEPRECATED"] = self.options.no_deprecated
        tc.variables["OPENSSL_NO_ENGINE"] = self.options.no_engine
        tc.generate()

    def build(self):
        """Build OpenSSL"""
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        # Run tests if enabled
        if self.options.enable_tests:
            cmake.test()

    def package(self):
        """Package OpenSSL"""
        # Copy headers
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.h", src=self.build_folder,
             dst=os.path.join(self.package_folder, "include"))

        # Copy libraries
        copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so*", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)

        # Copy executables
        copy(self, "openssl*", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)

        # Copy FIPS module if built
        if self.options.enable_fips:
            copy(self, "fips.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib/ossl-modules"), keep_path=False)
            copy(self, "fips.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)

        # Copy license and docs
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "CHANGES*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        # Generate SBOM for security compliance
        self._generate_sbom()

    def _calculate_file_hash(self, filepath, algorithm='sha256'):
        """Calculate cryptographic hash of a file"""
        hash_func = getattr(hashlib, algorithm)()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            self.output.warning(f"Failed to calculate hash for {filepath}: {e}")
            return None

    def _generate_sbom(self):
        """Generate Software Bill of Materials for security compliance"""
        self.output.info("Generating Software Bill of Materials (SBOM)...")

        file_hashes = {}
        for root, dirs, files in os.walk(self.package_folder):
            for file in files:
                if file.endswith(('.h', '.c', '.lib', '.a', '.so', '.dll', '.exe')):
                    file_path = os.path.join(root, file)
                    sha256 = self._calculate_file_hash(file_path, 'sha256')
                    if sha256:
                        rel_path = os.path.relpath(file_path, self.package_folder)
                        file_hashes[rel_path] = {
                            "sha256": sha256,
                            "algorithm": "SHA-256"
                        }

        build_metadata = {
            "build_timestamp": os.environ.get("SOURCE_DATE_EPOCH", ""),
            "build_platform": f"{self.settings.os}-{self.settings.arch}",
            "compiler": f"{self.settings.compiler}-{self.settings.compiler.version}",
            "build_type": str(self.settings.build_type),
            "fips_enabled": self.options.enable_fips,
            "conan_version": "2.0",
            "openssl_version": self.version
        }

        sbom_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": str(os.environ.get("SOURCE_DATE_EPOCH", "")),
                "component": {
                    "type": "library",
                    "bom-ref": f"{self.name}@{self.version}",
                    "name": self.name,
                    "version": str(self.version),
                    "description": self.description,
                    "licenses": [{"license": {"id": "Apache-2.0"}}],
                    "hashes": [{"alg": "SHA-256", "content": h["sha256"]}
                              for h in file_hashes.values()],
                    "externalReferences": [
                        {"type": "website", "url": self.homepage},
                        {"type": "vcs", "url": self.url}
                    ],
                    "properties": [
                        {"name": "build_metadata", "value": json.dumps(build_metadata)},
                        {"name": "fips_compliant", "value": str(self.options.enable_fips)},
                        {"name": "package_type", "value": "crypto-library"}
                    ]
                },
                "tools": [{"vendor": "Conan", "name": "conan", "version": "2.0"}]
            },
            "components": [],
            "vulnerabilities": []
        }

        # Save SBOM
        sbom_path = os.path.join(self.package_folder, "sbom.json")
        save(self, sbom_path, json.dumps(sbom_data, indent=2))
        self.output.success(f"SBOM generated: {sbom_path}")

    def package_info(self):
        """Package info for OpenSSL"""
        # Libraries
        if self.options.shared:
            self.cpp_info.libs = ["ssl", "crypto"]
        else:
            self.cpp_info.libs = ["ssl", "crypto"]

        # Paths
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]

        # FIPS-specific paths
        if self.options.enable_fips:
            self.cpp_info.libdirs.append("lib/ossl-modules")

        # Environment variables
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

        if self.settings.os == "Linux":
            self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        elif self.settings.os == "Macos":
            self.env_info.DYLD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        elif self.settings.os == "Windows":
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

        # FIPS configuration
        if self.options.enable_fips:
            fips_config = os.path.join(self.package_folder, "res", "fipsmodule.cnf")
            self.env_info.OPENSSL_FIPS = "1"
            self.env_info.OPENSSL_CONF = fips_config

    def package_id(self):
        """Optimize package ID for better caching"""
        # Test and docs options don't affect binary compatibility
        del self.info.options.enable_tests
        del self.info.options.enable_examples
        del self.info.options.enable_docs