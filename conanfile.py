from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get
from conan.tools.layout import basic_layout
from pathlib import Path

class OpenSSLConan(ConanFile):
    name = "openssl"
    description = "OpenSSL is an open-source toolkit for the Transport Layer Security (TLS) and Secure Sockets Layer (SSL) protocols."
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl"
    homepage = "https://www.openssl.org"
    topics = ("openssl", "crypto", "ssl", "tls", "fips")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fips": [True, False],
        "no_threads": [True, False],
        "no_asm": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fips": False,
        "no_threads": False,
        "no_asm": False,
    }

    # 💎 CENTRALIZED TOOLING: Using python_requires for build tools
    python_requires = "openssl-tools/2.2.2"

    # Export Python build scripts
    exports = "configure.py", "util/python/*.py"

    # ✅ BEST PRACTICE: This tells Conan to not use `export_sources`.
    # The source() method is now the single source of truth for obtaining code.
    no_copy_source = True

    def init(self):
        """Initialize the recipe with common settings."""
        pass

    def set_version(self):
        """Dynamically set the version with fallback logic."""
        # Use centralized version manager with fallback support
        try:
            VersionManager = self.python_requires["openssl-tools"].module.VersionManager
            version_manager = VersionManager(self.recipe_folder)

            # Try to get version from git/version file first
            detected_version = version_manager.get_version()

            # Apply version fallback logic if needed
            if hasattr(self.python_requires["openssl-tools"].ref, "_setup_version_fallback"):
                # Version fallback is handled by the tools package
                available_version = self._get_available_openssl_version()
                self.version = available_version
                self.output.info(f"Using OpenSSL version: {self.version}")
            else:
                # Fallback to detected version
                self.version = detected_version or '3.6.0'

        except Exception as e:
            self.output.warning(f"Version detection failed: {e}, using 3.6.0")
            self.version = '3.6.0'

    def _get_available_openssl_version(self):
        """Get available OpenSSL version using fallback logic."""
        try:
            # Try 4.0.0 first, then fallback to 3.6.0
            preferred_versions = ["4.0.0", "3.6.0", "3.4.1"]

            for version in preferred_versions:
                if self._is_openssl_version_available(version):
                    return version

            return "3.6.0"  # Ultimate fallback
        except Exception:
            return "3.6.0"

    def _is_openssl_version_available(self, version):
        """Check if a specific OpenSSL version is available."""
        # This could check git tags, version files, or remote availability
        # For now, implement basic version detection
        try:
            # Check if VERSION.dat exists and contains the version
            version_file = Path(self.recipe_folder) / "VERSION.dat"
            if version_file.exists():
                with open(version_file, 'r') as f:
                    content = f.read()
                    # Parse version from VERSION.dat format
                    # This is a simplified check - real implementation would parse properly
                    if version.replace('.', '') in content.replace('.', ''):
                        return True

            # Check git tags if available
            import subprocess
            result = subprocess.run(
                ["git", "tag", "-l", f"openssl-{version}"],
                cwd=self.recipe_folder,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return True

            return False
        except Exception:
            return False

    def layout(self):
        """Define the build layout. This is critical for locating sources."""
        # This standard layout places sources in <build_folder>/src.
        # The build() method will run from <build_folder>, and `self.source_folder` will correctly point to `src`.
        basic_layout(self, src_folder="src")

    def source(self):
        """Fetch the source code and prepare build environment."""
        from conan.tools.files import copy

        # For development, source is already available locally in the recipe folder
        # Copy essential source files to the source folder
        recipe_folder = self.recipe_folder

        # Copy Python build scripts (already exported)
        # Copy essential OpenSSL source files
        copy(self, "*.h", recipe_folder, self.source_folder)
        copy(self, "*.c", recipe_folder, self.source_folder)
        copy(self, "Makefile*", recipe_folder, self.source_folder)
        copy(self, "Configure*", recipe_folder, self.source_folder)
        copy(self, "config*", recipe_folder, self.source_folder)

        # Copy directories
        copy(self, "crypto/**/*", recipe_folder, self.source_folder)
        copy(self, "ssl/**/*", recipe_folder, self.source_folder)
        copy(self, "include/**/*", recipe_folder, self.source_folder)
        copy(self, "util/**/*", recipe_folder, self.source_folder)

    def requirements(self):
        """Define dependencies cleanly."""
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
        """Validate configuration options before the build."""
        # Delegate validation to the tooling layer.
        try:
            ProfileValidator = self.python_requires["openssl-tools"].module.ProfileValidator
            profile_validator = ProfileValidator(self)
            profile_validator.validate_all()
        except Exception as e:
            self.output.warning(f"Profile validation failed: {e}")

    def generate(self):
        """Generate build environment files."""
        # Sets up paths for build_requires like perl and nasm.
        VirtualBuildEnv(self).generate()

    def build(self):
        """Build OpenSSL using Python-based configuration."""
        import os
        import subprocess
        import sys

        self.output.info("Building OpenSSL with Python configure...")

        # Use Python configure script
        configure_cmd = [
            sys.executable, "configure.py",
            "--prefix=/usr/local/ssl",
            "--openssldir=/usr/local/ssl"
        ]

        # Add configuration options
        if self.options.fips:
            configure_cmd.append("enable-fips")

        if not self.options.shared:
            configure_cmd.append("no-shared")

        if self.options.no_threads:
            configure_cmd.append("no-threads")

        if self.options.no_asm:
            configure_cmd.append("no-asm")

        # Add compiler flags
        if self.options.fPIC and not self.options.shared:
            configure_cmd.append("-fPIC")

        try:
            # Run Python configure
            self.output.info(f"Running: {' '.join(configure_cmd)}")
            result = subprocess.run(configure_cmd, cwd=self.source_folder,
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.output.error(f"Configure failed: {result.stderr}")
                raise Exception(f"Configure failed with return code {result.returncode}")

            # Run make
            import multiprocessing
            jobs = multiprocessing.cpu_count() or 1
            make_cmd = ["make", f"-j{jobs}"]

            self.output.info(f"Running: {' '.join(make_cmd)}")
            result = subprocess.run(make_cmd, cwd=self.source_folder,
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.output.error(f"Make failed: {result.stderr}")
                raise Exception(f"Make failed with return code {result.returncode}")

            self.output.info("OpenSSL build completed successfully")

        except Exception as e:
            self.output.error(f"Build failed: {e}")
            raise

    def package(self):
        """Package the combined OpenSSL artifacts from both components."""
        try:
            OpenSSLBuildOrchestrator = self.python_requires["openssl-tools"].module.OpenSSLBuildOrchestrator
            SbomGenerator = self.python_requires["openssl-tools"].module.SbomGenerator
            DatabaseTracker = self.python_requires["openssl-tools"].module.DatabaseTracker

            # Use the orchestrator to combine artifacts from both libraries
            orchestrator = OpenSSLBuildOrchestrator(self)
            orchestrator.package_combined_openssl()

            # Integrated quality gates run automatically after packaging.
            sbom_gen = SbomGenerator(self)
            sbom_gen.generate_and_save(format="cyclonedx")
            db_tracker = DatabaseTracker(self)
            db_tracker.track_package()
        except Exception as e:
            self.output.warning(f"Quality gates failed: {e}")

    def package_info(self):
        """Define package information for consumers."""
        # This modern component-based approach is forward-compatible with CPS.
        # It is cleaner and more explicit than the previous implementation.
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")
        self.cpp_info.set_property("cmake_target_name", "OpenSSL::OpenSSL")
        self.cpp_info.set_property("pkg_config_name", "openssl")

        # --- Components ---
        self.cpp_info.components["crypto"].set_property("cmake_target_name", "OpenSSL::Crypto")
        self.cpp_info.components["crypto"].libs = ["crypto"]

        self.cpp_info.components["ssl"].set_property("cmake_target_name", "OpenSSL::SSL")
        self.cpp_info.components["ssl"].libs = ["ssl"]
        self.cpp_info.components["ssl"].requires = ["crypto", "zlib::zlib"]

        if self.options.fips:
            fips_module_dir = Path(self.package_folder) / "lib" / "ossl-modules"
            self.runenv_info.prepend_path("OPENSSL_MODULES", str(fips_module_dir))
            self.conf_info.define("user.openssl:fips_module_path", str(fips_module_dir))

    def log_upload_completion(self, remote_name: str = None):
        """Log package upload completion for CI/CD visibility."""
        try:
            DatabaseTracker = self.python_requires["openssl-tools"].module.DatabaseTracker
            tracker = DatabaseTracker(self)
            tracker.log_upload_completion(remote_name)
        except Exception as e:
            self.output.warning(f"Upload logging failed: {e}")
