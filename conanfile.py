#!/usr/bin/env python3
"""
OpenSSL Conan Package Recipe
Minimal implementation for upstream integration
"""

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy
import os


class OpenSSLConan(ConanFile):
    name = "openssl"
    
    def set_version(self):
        """Read version from VERSION.dat file"""
        version_file = os.path.join(self.recipe_folder, "VERSION.dat")
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                lines = f.readlines()
                major = minor = patch = "0"
                prerelease = ""
                for line in lines:
                    if line.startswith("MAJOR="):
                        major = line.split("=")[1].strip()
                    elif line.startswith("MINOR="):
                        minor = line.split("=")[1].strip()
                    elif line.startswith("PATCH="):
                        patch = line.split("=")[1].strip()
                    elif line.startswith("PRE_RELEASE_TAG="):
                        prerelease = line.split("=")[1].strip().strip('"')
                
                # Build version string
                version = f"{major}.{minor}.{patch}"
                if prerelease and prerelease != "":
                    version += f"-{prerelease}"
                self.version = version
        else:
            # Fallback version if VERSION.dat not found
            self.version = "4.0.3"

    # Package metadata
    description = "OpenSSL cryptographic library"
    homepage = "https://www.openssl.org"
    url = "https://github.com/sparesparrow/openssl"
    license = "Apache-2.0"
    topics = ("openssl", "crypto", "ssl", "tls")

    # Package configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
    }

    requires = [
        "openssl-base/1.0.1@sparesparrow/stable",
        "openssl-tools/1.2.4@sparesparrow/stable",
        "openssl-fips-data/140-3.2@sparesparrow/stable"
    ]

    def configure(self):
        """Configure package options"""
        # Static builds need fPIC
        if not self.options.shared:
            self.options.fPIC = True

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

    def source(self):
        """Get source code"""
        # Source is already available in the repository
        pass

    def build(self):
        """Build OpenSSL using traditional Configure/Make"""
        # Use OpenSSL's traditional build system (not CMake)
        self.output.info("Building OpenSSL using traditional Configure/Make build system")

        # Configure OpenSSL
        configure_cmd = "./Configure linux-x86_64 --prefix=/usr/local/ssl"
        if not self.options.shared:
            configure_cmd += " no-shared"
        if self.options.fPIC:
            configure_cmd += " -fPIC"

        self.run(configure_cmd, cwd=self.source_folder)

        # Build OpenSSL
        jobs = os.getenv("CONAN_CPU_COUNT", "1")
        self.run(f"make -j{jobs}", cwd=self.source_folder)

        # Run basic tests if enabled
        # if self.options.enable_fips:
        #     self.output.info("Running basic OpenSSL tests")
        #     self.run("make test", cwd=self.source_folder)

    def package(self):
        """Package OpenSSL properly to package folder"""
        # Install to a staging directory first
        staging = os.path.join(self.build_folder, "staging")
        self.run(f"make install DESTDIR={staging}", cwd=self.source_folder)
        
        # Copy from staging to package folder
        install_prefix = os.path.join(staging, "usr/local/ssl")
        
        # Libraries
        copy(self, "*.so*", src=os.path.join(install_prefix, "lib"), 
             dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", src=os.path.join(install_prefix, "lib"), 
             dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        
        # Headers
        copy(self, "*.h", src=os.path.join(install_prefix, "include"), 
             dst=os.path.join(self.package_folder, "include"), keep_path=True)
        
        # Binaries
        copy(self, "openssl", src=os.path.join(install_prefix, "bin"), 
             dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        
        # License
        copy(self, "LICENSE.txt", src=self.source_folder, 
             dst=os.path.join(self.package_folder, "licenses"))

        self.output.info("Packaging OpenSSL completed")

    def package_info(self):
        """Proper package info for CMake integration"""
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")
        self.cpp_info.set_property("cmake_target_name", "OpenSSL::OpenSSL")
        
        # Libraries
        self.cpp_info.libs = ["ssl", "crypto"]
        
        # Paths
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        
        # System dependencies
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "gdi32", "advapi32", "crypt32", "user32"])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.append("Security")
        
        # Environment
        self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))