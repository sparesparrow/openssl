"""
vcpkg Integration Module

Provides vcpkg integration utilities for OpenSSL builds.
"""

from .manager import VcpkgManager
from .integration import VcpkgIntegration
from .detector import VcpkgDetector

__all__ = [
    "VcpkgManager",
    "VcpkgIntegration",
    "VcpkgDetector"
]