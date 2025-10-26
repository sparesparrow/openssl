"""
OpenSSL Version Manager

Manages version parsing and generation for OpenSSL packages.
"""

import os
from pathlib import Path
from typing import Optional


class VersionManager:
    """Manages OpenSSL version parsing and generation."""

    def __init__(self, recipe_folder: str):
        """Initialize version manager with recipe folder path."""
        self.recipe_folder = Path(recipe_folder)

    def get_version(self) -> str:
        """Get version from VERSION.dat file or fallback to default."""
        version_file = self.recipe_folder / "VERSION.dat"

        if not version_file.exists():
            return "4.0.0-dev"

        try:
            version_data = self._parse_version_file(version_file)
            return self._format_version(version_data)
        except Exception:
            return "4.0.0-dev"

    def _parse_version_file(self, version_file: Path) -> dict:
        """Parse VERSION.dat file and return version components."""
        version_data = {}

        with open(version_file, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"')
                    version_data[key] = value

        return version_data

    def _format_version(self, version_data: dict) -> str:
        """Format version components into semantic version string."""
        major = version_data.get('MAJOR', '4')
        minor = version_data.get('MINOR', '0')
        patch = version_data.get('PATCH', '0')
        pre_release = version_data.get('PRE_RELEASE_TAG', '').strip()
        build_metadata = version_data.get('BUILD_METADATA', '').strip()

        # Build base version
        version = f"{major}.{minor}.{patch}"

        # Add pre-release tag if present
        if pre_release:
            version += f"-{pre_release}"

        # Add build metadata if present
        if build_metadata:
            version += f"+{build_metadata}"

        return version

    def get_openssl_version_info(self) -> dict:
        """Get complete version information including shlib version."""
        version_file = self.recipe_folder / "VERSION.dat"

        if not version_file.exists():
            return {
                "version": "4.0.0-dev",
                "shlib_version": "4",
                "major": "4",
                "minor": "0",
                "patch": "0"
            }

        try:
            version_data = self._parse_version_file(version_file)
            return {
                "version": self._format_version(version_data),
                "shlib_version": version_data.get('SHLIB_VERSION', '4'),
                "major": version_data.get('MAJOR', '4'),
                "minor": version_data.get('MINOR', '0'),
                "patch": version_data.get('PATCH', '0'),
                "pre_release_tag": version_data.get('PRE_RELEASE_TAG', ''),
                "build_metadata": version_data.get('BUILD_METADATA', ''),
                "release_date": version_data.get('RELEASE_DATE', '')
            }
        except Exception:
            return {
                "version": "4.0.0-dev",
                "shlib_version": "4",
                "major": "4",
                "minor": "0",
                "patch": "0"
            }