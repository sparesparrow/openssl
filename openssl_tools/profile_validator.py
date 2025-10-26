"""
OpenSSL Profile Validator

Validates Conan configuration options for OpenSSL builds.
"""

from conan.errors import ConanInvalidConfiguration


class ProfileValidator:
    """Validates OpenSSL configuration options."""

    def __init__(self, conanfile):
        """Initialize validator with conanfile instance."""
        self.conanfile = conanfile

    def validate_all(self):
        """Run all validation checks."""
        self._validate_fips_configuration()
        self._validate_threading_configuration()
        self._validate_asm_configuration()
        self._validate_shared_library_configuration()

    def _validate_fips_configuration(self):
        """Validate FIPS-related configuration options."""
        if self.conanfile.options.fips:
            # FIPS requires static linking for security
            if self.conanfile.options.shared:
                raise ConanInvalidConfiguration(
                    "FIPS mode requires static linking (shared=False) for security compliance"
                )

    def _validate_threading_configuration(self):
        """Validate threading configuration."""
        if self.conanfile.options.no_threads:
            # no_threads requires static linking
            if self.conanfile.options.shared:
                raise ConanInvalidConfiguration(
                    "no_threads option requires static linking (shared=False)"
                )

    def _validate_asm_configuration(self):
        """Validate assembly configuration."""
        if self.conanfile.options.no_asm:
            # no_asm requires static linking for compatibility
            if self.conanfile.options.shared:
                raise ConanInvalidConfiguration(
                    "no_asm option requires static linking (shared=False)"
                )

    def _validate_shared_library_configuration(self):
        """Validate shared library configuration across platforms."""
        # On Windows, shared libraries have different implications
        if self.conanfile.settings.os == "Windows":
            if self.conanfile.options.shared and self.conanfile.options.fPIC:
                # fPIC is not relevant on Windows for shared libraries
                self.conanfile.output.info(
                    "fPIC option ignored on Windows for shared libraries"
                )

        # On Linux/macOS, fPIC is required for shared libraries
        elif self.conanfile.settings.os in ["Linux", "Macos"]:
            if self.conanfile.options.shared and not self.conanfile.options.fPIC:
                raise ConanInvalidConfiguration(
                    "Shared libraries require fPIC=True on Unix-like systems"
                )

    def validate_build_requirements(self):
        """Validate that required build tools are available."""
        missing_tools = []

        if self.conanfile.settings.os == "Windows":
            # Check for required Windows build tools
            try:
                import subprocess
                # Check for nasm
                result = subprocess.run(["nasm", "-v"],
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    missing_tools.append("nasm")
            except FileNotFoundError:
                missing_tools.append("nasm")

            # Strawberry Perl should be handled by tool_requires
            # but we can check if it's in the path
            try:
                result = subprocess.run(["perl", "-v"],
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    missing_tools.append("perl")
            except FileNotFoundError:
                missing_tools.append("perl")

        if missing_tools:
            raise ConanInvalidConfiguration(
                f"Missing required build tools: {', '.join(missing_tools)}"
            )

    def get_validation_summary(self) -> dict:
        """Get summary of current validation state."""
        return {
            "fips_mode": self.conanfile.options.fips,
            "shared_linking": self.conanfile.options.shared,
            "threading_enabled": not self.conanfile.options.no_threads,
            "asm_enabled": not self.conanfile.options.no_asm,
            "fPIC_enabled": self.conanfile.options.fPIC,
            "platform": self.conanfile.settings.os,
            "compiler": self.conanfile.settings.compiler,
            "build_type": self.conanfile.settings.build_type
        }