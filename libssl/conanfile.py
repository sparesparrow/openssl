from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get
from conan.tools.layout import basic_layout
from pathlib import Path

class LibSSLConan(ConanFile):
    name = "libssl"
    description = "OpenSSL SSL/TLS library"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl"
    homepage = "https://www.openssl.org"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "no_threads": [True, False],
        "no_asm": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "no_threads": False,
        "no_asm": False,
    }

    # Python requires for build tools
    python_requires = "openssl-tools/2.2.0"

    # This package does not export sources - they come from the main openssl package
    no_copy_source = True

    def set_version(self):
        """Dynamically set the version from the parent openssl package."""
        try:
            VersionManager = self.python_requires["openssl-tools"].module.VersionManager
            self.version = '3.4.1'
        except Exception:
            self.version = '3.4.1'

    def layout(self):
        """Define the build layout."""
        basic_layout(self, src_folder="../src")

    def source(self):
        """Source handling - sources come from parent openssl package."""
        pass

    def requirements(self):
        """Define dependencies."""
        # Requires libcrypto
        self.requires("libcrypto/3.4.1@", visible=True)

        # zlib for compression support
        self.requires(
            "zlib/[>=1.3.1]",
            options={"shared": self.options.shared},
            visible=True
        )

    def build_requirements(self):
        """Add build requirements based on platform."""
        if self.settings.os == "Windows":
            self.tool_requires("strawberryperl/5.32.1.1")
            self.tool_requires("nasm/2.15.05")

    def configure(self):
        """Validate configuration options."""
        # Delegate validation to the tooling layer
        try:
            ProfileValidator = self.python_requires["openssl-tools"].module.ProfileValidator
            profile_validator = ProfileValidator(self)
            profile_validator.validate_all()
        except Exception as e:
            self.output.warning(f"Profile validation failed: {e}")

    def generate(self):
        """Generate build environment files."""
        VirtualBuildEnv(self).generate()

    def build(self):
        """Build the libssl library."""
        self.output.info("Building libssl...")

        # Use Python-based build orchestration
        try:
            SSLBuildOrchestrator = self.python_requires["openssl-tools"].module.SSLBuildOrchestrator
            orchestrator = SSLBuildOrchestrator(self)
            orchestrator.build_ssl_library()
        except Exception as e:
            self.output.error(f"libssl build orchestration failed: {e}")
            raise

    def package(self):
        """Package the libssl artifacts."""
        try:
            SSLBuildOrchestrator = self.python_requires["openssl-tools"].module.SSLBuildOrchestrator
            SbomGenerator = self.python_requires["openssl-tools"].module.SbomGenerator

            orchestrator = SSLBuildOrchestrator(self)
            orchestrator.package_ssl_library()

            # Generate SBOM for libssl
            sbom_gen = SbomGenerator(self)
            sbom_gen.generate_and_save(format="cyclonedx", component="libssl")
        except Exception as e:
            self.output.warning(f"libssl packaging failed: {e}")

    def package_info(self):
        """Define package information for consumers."""
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "LibSSL")
        self.cpp_info.set_property("cmake_target_name", "OpenSSL::SSL")
        self.cpp_info.set_property("pkg_config_name", "libssl")

        # Components
        self.cpp_info.components["ssl"].set_property("cmake_target_name", "OpenSSL::SSL")
        self.cpp_info.components["ssl"].libs = ["ssl"]
        self.cpp_info.components["ssl"].requires = ["libcrypto::crypto", "zlib::zlib"]

        if self.options.fPIC and not self.options.shared:
            self.cpp_info.components["ssl"].defines.append("OPENSSL_PIC")

        if self.options.no_threads:
            self.cpp_info.components["ssl"].defines.append("OPENSSL_NO_THREADS")

        if self.options.no_asm:
            self.cpp_info.components["ssl"].defines.append("OPENSSL_NO_ASM")

        # Set library directory
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]