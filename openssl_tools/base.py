"""
OpenSSL Recipe Base Classes

Provides base classes for OpenSSL Conan recipes.
"""

from conan import ConanFile
from conan.tools.layout import basic_layout
from pathlib import Path


class OpenSSLRecipeBase(ConanFile):
    """Base class for OpenSSL recipes providing common functionality."""

    def init(self):
        """Initialize the recipe with common settings."""
        pass

    def layout(self):
        """Define the build layout."""
        basic_layout(self, src_folder="src")

    def _get_optimal_cpu_count(self) -> int:
        """Get optimal number of CPU cores for building."""
        import multiprocessing
        import os

        cpu_count = multiprocessing.cpu_count() or 1

        # In CI environments, use all available cores
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            return cpu_count

        # Locally, reserve some cores for system responsiveness
        reserved = 1 if cpu_count > 2 else 0
        return max(1, cpu_count - reserved)

    def _get_build_info(self) -> dict:
        """Get build information and status."""
        return {
            "os": str(self.settings.os),
            "arch": str(self.settings.arch),
            "compiler": str(self.settings.compiler),
            "build_type": str(self.settings.build_type),
            "options": {
                "shared": self.options.shared,
                "fPIC": self.options.fPIC,
                "fips": getattr(self.options, 'fips', False),
                "no_threads": getattr(self.options, 'no_threads', False),
                "no_asm": getattr(self.options, 'no_asm', False)
            }
        }