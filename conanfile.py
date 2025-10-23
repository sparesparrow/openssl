from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, chdir
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
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "fips": False,
    }

    requires = "zlib/1.3.1"
    python_requires = [
        "openssl-profiles/2.0.1",
        "openssl-tools/1.2.6"
    ]

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
        """Export OpenSSL source tree efficiently, excluding external Perl modules"""
        import shutil

        # Copy everything first
        copy(self, "*", src=self.recipe_folder, dst=self.export_sources_folder)

        # Then remove the problematic external directory
        external_dir = os.path.join(self.export_sources_folder, "external")
        if os.path.exists(external_dir):
            shutil.rmtree(external_dir)
            self.output.info("Excluded external Perl modules directory from export")

        # Explicitly exclude external directory to avoid Perl module issues
        # The external directory contains problematic Perl modules that cause Configure to fail

    def configure(self):
        """Configure package options"""
        if not self.options.shared:
            self.options.fPIC = True

    def generate(self):
        """Setup build environment"""
        env = VirtualBuildEnv(self)
        env.generate()

    def build(self):
        """Build OpenSSL using Configure + Make"""
        with chdir(self, self.source_folder):
            # Patch all Perl scripts to skip external Perl modules
            import glob

            # Find all Perl scripts that reference external/perl
            perl_scripts = []
            perl_scripts.append(os.path.join(self.source_folder, "Configure"))
            perl_scripts.extend(glob.glob(os.path.join(self.source_folder, "util", "*.pl")))
            perl_scripts.extend(glob.glob(os.path.join(self.source_folder, "util", "perl", "**", "*.pm"), recursive=True))

            for script_path in perl_scripts:
                if os.path.exists(script_path):
                    with open(script_path, 'r') as f:
                        script_content = f.read()

                    # Comment out lines that try to load external Perl modules
                    original_content = script_content
                    script_content = script_content.replace(
                        'use OpenSSL::fallback "$FindBin::Bin/external/perl/MODULES.txt";',
                        '# use OpenSSL::fallback "$FindBin::Bin/external/perl/MODULES.txt";  # Disabled by Conan'
                    )
                    script_content = script_content.replace(
                        'use OpenSSL::fallback "$FindBin::Bin/../external/perl/MODULES.txt";',
                        '# use OpenSSL::fallback "$FindBin::Bin/../external/perl/MODULES.txt";  # Disabled by Conan'
                    )

                    if script_content != original_content:
                        with open(script_path, 'w') as f:
                            f.write(script_content)
                        self.output.info(f"Patched {os.path.basename(script_path)} to skip external Perl modules")

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

            # Set environment variables for Configure
            env_vars = [
                "PERL=/usr/bin/perl",  # Use system Perl
                f"OPENSSL_CONF_INCLUDE={os.path.join(self.source_folder, 'Configurations')}",
                "PERL5LIB=",  # Clear Perl library path to avoid external modules
                "PERLLIB=",   # Clear Perl library path to avoid external modules
                "OPENSSL_NO_EXTERNAL_PERL=1"  # Disable external Perl modules
            ]

            # Run Configure (generates Makefile, NOT build.ninja)
            self.run(" ".join(configure_args), env=env_vars)

            # Build with make (official OpenSSL backend)
            # Use fewer parallel jobs to avoid dependency file conflicts
            self.run(f"make -j{min(4, os.cpu_count() or 1)}", env=env_vars)

    def package(self):
        """Install OpenSSL"""
        with chdir(self, self.source_folder):
            self.run("make install")

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

        # System dependencies
        if self.settings.os == "Linux":
            crypto.system_libs = ["dl", "pthread"]
        elif self.settings.os == "Windows":
            crypto.system_libs = ["advapi32", "crypt32", "user32"]
            ssl.system_libs = ["ws2_32", "gdi32"]
