from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, chdir, get, replace_in_file
from conan.tools.layout import basic_layout
import os

class OpenSSLConan(ConanFile):
    name = "openssl"
    description = "OpenSSL cryptographic library"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl"
    homepage = "https://www.openssl.org"
    topics = ("openssl", "crypto", "ssl", "tls")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fips": [True, False],
        "no_threads": [True, False],
        "no_asm": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "fips": False,
        "no_threads": False,
        "no_asm": False,
    }

    requires = "zlib/1.3.1"
    python_requires = [
        "openssl-profiles/2.0.1",
        "openssl-tools/1.2.6"
    ]

    def layout(self):
        basic_layout(self)

    def set_version(self):
        """Read version from VERSION.dat"""
        version_file = os.path.join(self.recipe_folder, "VERSION.dat")
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                version_data = {}
                for line in f:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        version_data[key.strip()] = value.strip().strip('"')

                version = f"{version_data.get('MAJOR', '4')}.{version_data.get('MINOR', '0')}.{version_data.get('PATCH', '0')}"
                prerelease = version_data.get('PRE_RELEASE_TAG', '')
                if prerelease:
                    version += f"-{prerelease}"
                self.version = version
        else:
            self.version = "4.0.1-dev"

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

    def configure(self):
        """Configure package options"""
        if not self.options.shared:
            self.options.fPIC = True

    def build_requirements(self):
        """Add build requirements based on platform"""
        if self.settings.os == "Windows":
            self.tool_requires("strawberryperl/5.32.1.1")
            self.tool_requires("nasm/2.15.05")
        # On Unix systems, assume Perl and make are available as system packages

    def generate(self):
        """Setup build environment"""
        env = VirtualBuildEnv(self)
        env.generate()

    def build(self):
        """Build OpenSSL using build orchestrator"""
        # Get the OpenSSL tools for build orchestration
        try:
            from openssl_tools.foundation import OpenSSLBuildOrchestrator
            orchestrator = OpenSSLBuildOrchestrator(self)
            orchestrator.configure_and_build()
        except ImportError:
            # Fallback to manual build if tools not available
            self._manual_build()

    def _manual_build(self):
        """Manual build process as fallback"""
        with chdir(self, self.source_folder):
            # Platform-specific Configure target
            target_map = {
                ("Linux", "x86_64"): "linux-x86_64",
                ("Linux", "x86"): "linux-x86",
                ("Windows", "x86_64"): "VC-WIN64A",
                ("Windows", "x86"): "VC-WIN32",
                ("Macos", "armv8"): "darwin64-arm64-cc",
                ("Macos", "x86_64"): "darwin64-x86_64-cc",
            }
            target = target_map.get((str(self.settings.os), str(self.settings.arch)), "linux-x86_64")

            # Build Configure command
            configure_args = [
                "./Configure",
                target,
                f"--prefix={self.package_folder}",
                f"--openssldir={self.package_folder}",
            ]

            if self.options.fips:
                configure_args.append("enable-fips")

            if not self.options.shared:
                configure_args.append("no-shared")

            if self.options.no_threads:
                configure_args.append("no-threads")

            if self.options.no_asm:
                configure_args.append("no-asm")

            # Set environment variables for Configure
            env_vars = [
                "PERL=perl",  # Use system Perl
                f"OPENSSL_CONF_INCLUDE={os.path.join(self.source_folder, 'Configurations')}",
            ]

            # Run Configure (generates Makefile, NOT build.ninja)
            self.run(configure_args, env=env_vars)

            # Build with make (official OpenSSL backend)
            # Use fewer parallel jobs to avoid dependency file conflicts
            import multiprocessing
            cpu_count = min(4, multiprocessing.cpu_count() or 1)
            self.run(f"make -j{cpu_count}", env=env_vars)

    def package(self):
        """Install OpenSSL"""
        try:
            from openssl_tools.foundation import OpenSSLBuildOrchestrator
            orchestrator = OpenSSLBuildOrchestrator(self)
            orchestrator.install_openssl()
        except ImportError:
            # Fallback to manual install if tools not available
            with chdir(self, self.source_folder):
                self.run(f"make install DESTDIR={self.package_folder}")

        # Copy licenses
        copy(self, "LICENSE*", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"), keep_path=False)



    def package_info(self):
        """Configure CMake targets for OpenSSL components"""
        # Modern CMake package properties
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")
        self.cpp_info.set_property("cmake_target_name", "OpenSSL::OpenSSL")

        # SSL component configuration
        ssl = self.cpp_info.components["ssl"]
        ssl.set_property("cmake_target_name", "OpenSSL::SSL")
        ssl.libs = ["ssl"]  # ← CRITICAL: Maps to libssl.a/libssl.so
        ssl.requires = ["crypto"]

        # Crypto component configuration
        crypto = self.cpp_info.components["crypto"]
        crypto.set_property("cmake_target_name", "OpenSSL::Crypto")
        crypto.libs = ["crypto"]  # ← CRITICAL: Maps to libcrypto.a/libcrypto.so

        # Legacy CMake module support
        self.cpp_info.names["cmake_find_package"] = "OpenSSL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenSSL"

        # Root package (for legacy consumers)
        self.cpp_info.libs = ["ssl", "crypto"]

        # Directories
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = ["lib64", "lib"]
        self.cpp_info.includedirs = ["include"]

        # System dependencies
        if self.settings.os == "Linux":
            crypto.system_libs = ["dl", "pthread"]
        elif self.settings.os == "Windows":
            crypto.system_libs = ["advapi32", "crypt32", "user32"]
            ssl.system_libs = ["ws2_32", "gdi32"]
