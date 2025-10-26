"""
OpenSSL Build Orchestrator

Orchestrates the complete OpenSSL build process including configure, build, and install phases.
"""

import os
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, Optional


class OpenSSLBuildOrchestrator:
    """Orchestrates OpenSSL build process."""

    def __init__(self, conanfile):
        """Initialize orchestrator with conanfile instance."""
        self.conanfile = conanfile
        self.source_folder = Path(conanfile.source_folder)
        self.build_folder = Path(conanfile.build_folder)
        self.package_folder = Path(conanfile.package_folder)

        # In development mode, source might be in the recipe folder
        self.recipe_folder = Path(conanfile.recipe_folder)
        self.actual_source_dir = self._determine_source_directory()

    def _determine_source_directory(self) -> Path:
        """Determine the correct source directory to use."""
        # Check if Configure script exists in source_folder
        if (self.source_folder / "Configure").exists():
            return self.source_folder

        # Check if Configure script exists in recipe_folder (development mode)
        if (self.recipe_folder / "Configure").exists():
            return self.recipe_folder

        # Default to source_folder
        return self.source_folder

    def configure_and_build(self):
        """Configure and build OpenSSL."""
        self.conanfile.output.info("Starting OpenSSL build orchestration...")

        # Ensure we're in the correct source directory for configuration
        original_cwd = os.getcwd()
        try:
            os.chdir(self.actual_source_dir)

            # Configure OpenSSL
            if not self._configure_openssl():
                raise Exception("OpenSSL configuration failed")

            # Build OpenSSL
            if not self._build_openssl():
                raise Exception("OpenSSL build failed")

            # Run tests if not skipped
            if not self._should_skip_tests():
                if not self._test_openssl():
                    self.conanfile.output.warn("OpenSSL tests failed, continuing with packaging")

        finally:
            os.chdir(original_cwd)

    def install_and_package(self):
        """Install OpenSSL to package directory."""
        self.conanfile.output.info("Starting OpenSSL packaging...")

        # Create staging directory
        staging_dir = self.build_folder / "staging"
        staging_dir.mkdir(exist_ok=True)

        # Ensure we're in the build directory for installation
        original_cwd = os.getcwd()
        try:
            os.chdir(self.source_folder)

            # Install to staging directory
            if not self._install_openssl(str(staging_dir)):
                raise Exception("OpenSSL installation failed")

            # Copy from staging to package folder
            self._copy_to_package_folder(staging_dir)

        finally:
            os.chdir(original_cwd)

    def _configure_openssl(self) -> bool:
        """Configure OpenSSL build using Python configure script."""
        self.conanfile.output.info("Configuring OpenSSL with Python configure...")

        # Use Python configure script instead of Perl
        configure_cmd = self._build_python_configure_command()

        try:
            result = subprocess.run(configure_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                self.conanfile.output.error(f"Python configure failed: {result.stderr}")
                return False

            self.conanfile.output.info("OpenSSL Python configuration completed successfully")
            return True

        except Exception as e:
            self.conanfile.output.error(f"Configure exception: {e}")
            return False

    def _build_openssl(self) -> bool:
        """Build OpenSSL."""
        self.conanfile.output.info("Building OpenSSL...")

        try:
            # Run make
            make_cmd = f"make -j{self._get_optimal_job_count()}"
            result = subprocess.run(make_cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                self.conanfile.output.error(f"Build failed: {result.stderr}")
                return False

            self.conanfile.output.info("OpenSSL build completed successfully")
            return True

        except Exception as e:
            self.conanfile.output.error(f"Build exception: {e}")
            return False

    def _test_openssl(self) -> bool:
        """Test OpenSSL build."""
        self.conanfile.output.info("Testing OpenSSL...")

        try:
            # Run tests
            test_cmd = "make test"
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                self.conanfile.output.warn(f"Tests failed: {result.stderr}")
                return False

            self.conanfile.output.info("OpenSSL tests passed")
            return True

        except Exception as e:
            self.conanfile.output.warn(f"Test exception: {e}")
            return False

    def _install_openssl(self, install_dir: str) -> bool:
        """Install OpenSSL to specified directory."""
        self.conanfile.output.info(f"Installing OpenSSL to {install_dir}...")

        try:
            # Run make install with DESTDIR
            install_cmd = f"make install DESTDIR={install_dir}"
            result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                self.conanfile.output.error(f"Install failed: {result.stderr}")
                return False

            self.conanfile.output.info("OpenSSL installation completed successfully")
            return True

        except Exception as e:
            self.conanfile.output.error(f"Install exception: {e}")
            return False

    def _build_python_configure_command(self) -> str:
        """Build the Python configure command for OpenSSL."""
        target = self._get_configure_target()

        # Build command parts for Python configure script
        cmd_parts = [
            "python3",
            "configure.py",
            target
        ]

        # Add configuration options (Python configure uses different syntax)
        if self.conanfile.options.fips:
            cmd_parts.append("enable-fips")

        if not self.conanfile.options.shared:
            cmd_parts.append("no-shared")

        if self.conanfile.options.no_threads:
            cmd_parts.append("no-threads")

        if self.conanfile.options.no_asm:
            cmd_parts.append("no-asm")

        # Add compiler flags
        if self.conanfile.options.fPIC and not self.conanfile.options.shared:
            cmd_parts.append("-fPIC")

        # Add prefix options
        cmd_parts.extend([
            f"--prefix=/usr/local/ssl",  # This will be prefixed by DESTDIR
            f"--openssldir=/usr/local/ssl"
        ])

        return " ".join(cmd_parts)

    def _get_configure_target(self) -> str:
        """Get the Configure target for the current platform."""
        os_name = self.conanfile.settings.os
        arch = self.conanfile.settings.arch

        target_map = {
            ("Linux", "x86_64"): "linux-x86_64",
            ("Linux", "x86"): "linux-x86",
            ("Linux", "armv8"): "linux-aarch64",
            ("Macos", "x86_64"): "darwin64-x86_64-cc",
            ("Macos", "armv8"): "darwin64-arm64-cc",
            ("Windows", "x86_64"): "VC-WIN64A",
            ("Windows", "x86"): "VC-WIN32",
        }

        return target_map.get((str(os_name), str(arch)), "linux-x86_64")

    def _get_optimal_job_count(self) -> int:
        """Get optimal number of parallel jobs for building."""
        import multiprocessing

        cpu_count = multiprocessing.cpu_count() or 1

        # In CI environments, use all available cores
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            return cpu_count

        # Locally, reserve some cores for system responsiveness
        reserved = 1 if cpu_count > 2 else 0
        return max(1, cpu_count - reserved)

    def _should_skip_tests(self) -> bool:
        """Determine if tests should be skipped."""
        # Skip tests in CI if explicitly requested
        if os.getenv('SKIP_OPENSSL_TESTS'):
            return True

        # Skip tests for cross-compilation
        if hasattr(self.conanfile.settings, 'os') and hasattr(self.conanfile.settings, 'arch'):
            host_os = platform.system().lower()
            target_os = str(self.conanfile.settings.os).lower()
            if host_os != target_os:
                self.conanfile.output.info("Skipping tests for cross-compilation")
                return True

        return False

    def _copy_to_package_folder(self, staging_dir: Path):
        """Copy installed files from staging to package folder."""
        import shutil

        self.conanfile.output.info("Copying files to package folder...")

        # Copy lib, include, bin directories
        for subdir in ["lib", "include", "bin", "share"]:
            src_dir = staging_dir / "usr" / "local" / "ssl" / subdir
            dst_dir = self.package_folder / subdir

            if src_dir.exists():
                if dst_dir.exists():
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
                self.conanfile.output.info(f"Copied {subdir} directory")

        # Copy licenses
        licenses_src = self.source_folder / "LICENSE.txt"
        licenses_dst = self.package_folder / "licenses" / "LICENSE.txt"
        licenses_dst.parent.mkdir(parents=True, exist_ok=True)

        if licenses_src.exists():
            shutil.copy2(licenses_src, licenses_dst)
            self.conanfile.output.info("Copied license file")


class CryptoBuildOrchestrator:
    """Orchestrates building of the libcrypto component."""

    def __init__(self, conanfile):
        """Initialize orchestrator with conanfile instance."""
        self.conanfile = conanfile
        self.source_folder = Path(conanfile.source_folder)
        self.build_folder = Path(conanfile.build_folder)
        self.package_folder = Path(conanfile.package_folder)

    def build_crypto_library(self):
        """Build the libcrypto library component."""
        self.conanfile.output.info("Building libcrypto component...")

        # Use Python-based build system
        # This would integrate with the Python configure and make system
        # For now, delegate to the main orchestrator
        main_orchestrator = OpenSSLBuildOrchestrator(self.conanfile)
        main_orchestrator.configure_and_build()

    def package_crypto_library(self):
        """Package the libcrypto library artifacts."""
        self.conanfile.output.info("Packaging libcrypto component...")

        # Package only crypto-related files
        # This would filter and copy only libcrypto artifacts
        main_orchestrator = OpenSSLBuildOrchestrator(self.conanfile)
        main_orchestrator.install_and_package()


class SSLBuildOrchestrator:
    """Orchestrates building of the libssl component."""

    def __init__(self, conanfile):
        """Initialize orchestrator with conanfile instance."""
        self.conanfile = conanfile
        self.source_folder = Path(conanfile.source_folder)
        self.build_folder = Path(conanfile.build_folder)
        self.package_folder = Path(conanfile.package_folder)

    def build_ssl_library(self):
        """Build the libssl library component."""
        self.conanfile.output.info("Building libssl component...")

        # Use Python-based build system
        # This would integrate with the Python configure and make system
        # For now, delegate to the main orchestrator
        main_orchestrator = OpenSSLBuildOrchestrator(self.conanfile)
        main_orchestrator.configure_and_build()

    def package_ssl_library(self):
        """Package the libssl library artifacts."""
        self.conanfile.output.info("Packaging libssl component...")

        # Package only ssl-related files
        # This would filter and copy only libssl artifacts
        main_orchestrator = OpenSSLBuildOrchestrator(self.conanfile)
        main_orchestrator.install_and_package()

    def package_combined_openssl(self):
        """Package combined OpenSSL artifacts from both libcrypto and libssl."""
        self.conanfile.output.info("Packaging combined OpenSSL...")

        # Create staging directory
        staging_dir = self.build_folder / "combined_staging"
        staging_dir.mkdir(exist_ok=True)

        # This would combine artifacts from both libcrypto and libssl packages
        # For now, use the standard install approach
        self.install_and_package()