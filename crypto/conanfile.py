from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout
from pathlib import Path

class CryptoConan(ConanFile):
    name = "crypto"
    description = "OpenSSL crypto library component"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl"
    homepage = "https://www.openssl.org"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "no_threads": [True, False],
        "no_asm": [True, False],
        "fips": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "no_threads": False,
        "no_asm": False,
        "fips": False,
    }

    # Python requires for build tools
    python_requires = "openssl-tools/2.2.0"

    # This package does not export sources - they come from the main openssl package
    no_copy_source = True

    def set_version(self):
        """Dynamically set the version."""
        try:
            VersionManager = self.python_requires["openssl-tools"].module.VersionManager
            self.version = '3.4.1'
        except Exception:
            self.version = '3.4.1'

    def layout(self):
        """Define the build layout."""
        basic_layout(self, src_folder="..")

    def source(self):
        """Source handling."""
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
        """Add build requirements."""
        if self.settings.os == "Windows":
            self.tool_requires("strawberryperl/5.32.1.1")
            self.tool_requires("nasm/2.15.05")

    def configure(self):
        """Validate configuration."""
        try:
            ProfileValidator = self.python_requires["openssl-tools"].module.ProfileValidator
            profile_validator = ProfileValidator(self)
            profile_validator.validate_all()
        except Exception as e:
            self.output.warning(f"Profile validation failed: {e}")

    def generate(self):
        """Generate build environment."""
        VirtualBuildEnv(self).generate()

    def build(self):
        """Build the crypto component."""
        self.output.info("Building crypto component...")

        # Use Python-based build orchestration
        try:
            CryptoComponentBuilder = self.python_requires["openssl-tools"].module.CryptoComponentBuilder
            builder = CryptoComponentBuilder(self)
            builder.build_crypto_component()
        except Exception as e:
            self.output.error(f"Crypto component build failed: {e}")
            raise

    def package(self):
        """Package the crypto component artifacts."""
        try:
            CryptoComponentBuilder = self.python_requires["openssl-tools"].module.CryptoComponentBuilder
            SbomGenerator = self.python_requires["openssl-tools"].module.SbomGenerator

            builder = CryptoComponentBuilder(self)
            builder.package_crypto_component()

            # Generate SBOM
            sbom_gen = SbomGenerator(self)
            sbom_gen.generate_and_save(format="cyclonedx", component="crypto")
        except Exception as e:
            self.output.warning(f"Crypto packaging failed: {e}")

    def package_info(self):
        """Define package information."""
        self.cpp_info.libs = ["crypto"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]

        if self.options.fPIC and not self.options.shared:
            self.cpp_info.defines.append("OPENSSL_PIC")

        if self.options.no_threads:
            self.cpp_info.defines.append("OPENSSL_NO_THREADS")

        if self.options.no_asm:
            self.cpp_info.defines.append("OPENSSL_NO_ASM")

        if self.options.fips:
            self.cpp_info.defines.append("OPENSSL_FIPS")