from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import copy
import os
import json

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
            self.version = "4.0.4"

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
        "fips": [True, False],
        "no_threads": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "fips": False,
        "no_threads": False,
    }

    requires = [
        "openssl-profiles/2.0.2",  # Merged base + fips
    ]

    python_requires = [
        "openssl-conan-base/1.0.1@sparesparrow/stable",  # Foundation layer
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
        # In-tree, zdroje již přítomny
        pass

    def generate(self):
        """Generate build files using modern CMake integration (CppCon 2024 approach)"""
        # Use Python configure.py to generate Makefile and CPS file
        configure_cmd = "python3 configure.py"
        configure_args = [
            "linux-x86_64",  # Target platform
        ]

        if self.options.shared:
            configure_args.append("shared")
        else:
            configure_args.append("no-shared")

        if self.options.no_threads:
            configure_args.append("no-threads")

        if self.options.fips:
            configure_args.append("enable-fips")

        if not self.options.fPIC:
            configure_args.append("no-pic")

        # Run Python configure (generates Makefile and CPS file)
        self.run(f"{configure_cmd} {' '.join(configure_args)}", cwd=self.source_folder)

        # Generate CMake toolchain for consumers
        tc = CMakeToolchain(self)
        tc.variables["OPENSSL_ROOT_DIR"] = "/usr/local/ssl"
        tc.variables["OPENSSL_SHARED"] = self.options.shared
        tc.variables["OPENSSL_FIPS"] = self.options.fips
        tc.variables["OPENSSL_NO_THREADS"] = self.options.no_threads
        tc.generate()

        # Generate CMake dependencies
        deps = CMakeDeps(self)
        deps.set_property("openssl", "cmake_target_name", "OpenSSL::OpenSSL")
        deps.generate()

    def build(self):
        """Build OpenSSL using proper build commands"""
        self.output.info("Building OpenSSL...")

        # For now, let's use the traditional OpenSSL build approach
        # since the Python configure.py is just a stub
        if not os.path.exists(os.path.join(self.source_folder, "Makefile")):
            # Fall back to traditional configure if Makefile doesn't exist
            configure_cmd = "./Configure"
            configure_args = [
                "linux-x86_64",
                "shared",
                "--prefix=/usr/local/ssl",
                "--openssldir=/usr/local/ssl",
            ]

            self.run(f"{configure_cmd} {' '.join(configure_args)}", cwd=self.source_folder)

        # Build using make
        self.run("make", cwd=self.source_folder)

    def package(self):
        """Package OpenSSL properly to package folder"""
        # For now, let's copy the built artifacts directly from the build directory
        # since the make install isn't working in the container environment

        # Copy libraries from build directory (they should be in the build root or lib/)
        lib_patterns = ["*.so*", "*.a", "libssl*", "libcrypto*"]
        for pattern in lib_patterns:
            copy(self, pattern, src=self.build_folder,
                 dst=os.path.join(self.package_folder, "lib"), keep_path=False)

        # Copy headers
        copy(self, "*.h", src=os.path.join(self.build_folder, "include"),
             dst=os.path.join(self.package_folder, "include"), keep_path=True)

        # Copy openssl binary
        copy(self, "openssl", src=os.path.join(self.build_folder, "apps"),
             dst=os.path.join(self.package_folder, "bin"), keep_path=False)

        # License
        copy(self, "LICENSE.txt", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

        self.output.info("Packaging OpenSSL completed")

    def package_info(self):
        """Proper package info for CMake integration with modern Conan 2.x approach"""
        # Main OpenSSL target
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")
        self.cpp_info.set_property("cmake_target_name", "OpenSSL::OpenSSL")

        # Libraries in correct dependency order (ssl depends on crypto)
        self.cpp_info.libs = ["ssl", "crypto"]

        # Paths
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]

        # System dependencies based on platform
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "gdi32", "advapi32", "crypt32", "user32"]
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "Security"]

        # Define components for better CMake integration (following CppCon modular approach)
        # SSL component
        self.cpp_info.components["ssl"].libs = ["ssl"]
        self.cpp_info.components["ssl"].requires = ["crypto"]
        self.cpp_info.components["ssl"].set_property("cmake_target_name", "OpenSSL::SSL")

        # Crypto component
        self.cpp_info.components["crypto"].libs = ["crypto"]
        self.cpp_info.components["crypto"].set_property("cmake_target_name", "OpenSSL::Crypto")

        # Environment variables for runtime
        self.runenv_info.append_path("PATH", "bin")

        # Generate CPS file for modern build system interoperability
        self._generate_cps_file()

    def _generate_cps_file(self):
        """Generate Common Package Specification file for build system interoperability"""
        cps_data = {
            "cps_version": "0.13.0",
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "license": self.license,
            "components": {
                "crypto": {
                    "type": "library",
                    "location": "@prefix@/lib/libcrypto.a",
                    "includes": ["@prefix@/include"],
                    "defines": ["OPENSSL_USE_NODELETE"] if self.options.shared else []
                },
                "ssl": {
                    "type": "library",
                    "location": "@prefix@/lib/libssl.a",
                    "includes": ["@prefix@/include"],
                    "requires": ["crypto"],
                    "defines": ["OPENSSL_USE_NODELETE"] if self.options.shared else []
                }
            },
            "properties": {
                "cmake_find_module_name": "OpenSSL",
                "cmake_target:crypto": "OpenSSL::Crypto",
                "cmake_target:ssl": "OpenSSL::SSL",
                "cmake_target:openssl": "OpenSSL::OpenSSL"
            },
            "system_libs": self._get_system_libs(),
            "frameworks": self._get_frameworks()
        }

        # Write CPS file to package folder
        cps_file = os.path.join(self.package_folder, f"{self.name}.cps")
        with open(cps_file, 'w') as f:
            json.dump(cps_data, f, indent=2)

        self.output.info(f"Generated CPS file: {cps_file}")

    def _get_system_libs(self):
        """Get system libraries based on platform"""
        if self.settings.os == "Linux":
            return ["dl", "pthread"]
        elif self.settings.os == "Windows":
            return ["ws2_32", "gdi32", "advapi32", "crypt32", "user32"]
        return []

    def _get_frameworks(self):
        """Get frameworks for macOS"""
        if self.settings.os == "Macos":
            return ["CoreFoundation", "Security"]
        return []
