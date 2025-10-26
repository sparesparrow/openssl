from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get
from conan.tools.layout import basic_layout
from pathlib import Path

class LibCryptoConan(ConanFile):
    name = "libcrypto"
    description = "OpenSSL core cryptographic library"
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
        # This would typically read from the parent package or a shared version file
        # For now, use a fixed version that matches the main package
        try:
            VersionManager = self.python_requires["openssl-tools"].module.VersionManager
            # Try to read from a shared location or use a default
            self.version = '3.4.1'
        except Exception:
            self.version = '3.4.1'

    def layout(self):
        """Define the build layout."""
        basic_layout(self, src_folder="../src")

    def source(self):
        """Source handling - sources come from parent openssl package."""
        # In a real implementation, this might reference the parent package
        # For now, assume sources are available in the parent directory
        pass

    def requirements(self):
        """Define dependencies."""
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
        """Build the libcrypto library."""
        self.output.info("Building libcrypto...")

        # Use Python-based build orchestration
        try:
            CryptoBuildOrchestrator = self.python_requires["openssl-tools"].module.CryptoBuildOrchestrator
            orchestrator = CryptoBuildOrchestrator(self)
            orchestrator.build_crypto_library()
        except Exception as e:
            self.output.error(f"libcrypto build orchestration failed: {e}")
            raise

    def package(self):
        """Package the libcrypto artifacts."""
        try:
            CryptoBuildOrchestrator = self.python_requires["openssl-tools"].module.CryptoBuildOrchestrator
            SbomGenerator = self.python_requires["openssl-tools"].module.SbomGenerator

            orchestrator = CryptoBuildOrchestrator(self)
            orchestrator.package_crypto_library()

            # Generate SBOM for libcrypto
            sbom_gen = SbomGenerator(self)
            sbom_gen.generate_and_save(format="cyclonedx", component="libcrypto")
        except Exception as e:
            self.output.warning(f"libcrypto packaging failed: {e}")

    def package_info(self):
        """Define package information for consumers."""
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "LibCrypto")
        self.cpp_info.set_property("cmake_target_name", "OpenSSL::Crypto")
        self.cpp_info.set_property("pkg_config_name", "libcrypto")

        # Components
        self.cpp_info.components["crypto"].set_property("cmake_target_name", "OpenSSL::Crypto")
        self.cpp_info.components["crypto"].libs = ["crypto"]
        self.cpp_info.components["crypto"].requires = ["zlib::zlib"]

        if self.options.fPIC and not self.options.shared:
            self.cpp_info.components["crypto"].defines.append("OPENSSL_PIC")

        if self.options.no_threads:
            self.cpp_info.components["crypto"].defines.append("OPENSSL_NO_THREADS")

        if self.options.no_asm:
            self.cpp_info.components["crypto"].defines.append("OPENSSL_NO_ASM")

        # Set library directory
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]