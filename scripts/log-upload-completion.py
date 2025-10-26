#!/usr/bin/env python3
"""
Log OpenSSL Package Upload Completion

This script logs package upload completion for CI/CD visibility.
Usage: python log-upload-completion.py [remote_name]
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point."""
    remote_name = sys.argv[1] if len(sys.argv) > 1 else None

    # Import after path setup
    from openssl_tools.database_tracker import DatabaseTracker

    # Create a mock conanfile-like object for logging
    class MockOutput:
        def info(self, msg):
            print(f"ℹ️  {msg}")

        def error(self, msg):
            print(f"❌ {msg}", file=sys.stderr)

        def warn(self, msg):
            print(f"⚠️  {msg}")

    class MockConanFile:
        def __init__(self):
            self.name = os.getenv('CONAN_PACKAGE_NAME', 'openssl')
            self.version = os.getenv('CONAN_PACKAGE_VERSION', '4.0.0-dev')
            self.user = os.getenv('CONAN_USER', 'unknown')
            self.channel = os.getenv('CONAN_CHANNEL', 'unknown')
            self.package_folder = os.getenv('CONAN_PACKAGE_FOLDER', './package')
            self.settings = MockSettings()
            self.options = MockOptions()
            self.output = MockOutput()

    class MockSettings:
        def __init__(self):
            self.os = os.getenv('CONAN_OS', 'Linux')
            self.arch = os.getenv('CONAN_ARCH', 'x86_64')
            self.build_type = os.getenv('CONAN_BUILD_TYPE', 'Release')
            self.compiler = os.getenv('CONAN_COMPILER', 'clang')

    class MockOptions:
        def __init__(self):
            self.shared = os.getenv('CONAN_SHARED', 'False').lower() == 'true'
            self.fips = os.getenv('CONAN_FIPS', 'False').lower() == 'true'
            self.no_threads = os.getenv('CONAN_NO_THREADS', 'False').lower() == 'true'
            self.no_asm = os.getenv('CONAN_NO_ASM', 'False').lower() == 'true'
            self.fPIC = os.getenv('CONAN_FPIC', 'True').lower() == 'true'

    # Create mock conanfile and log upload completion
    mock_conanfile = MockConanFile()
    tracker = DatabaseTracker(mock_conanfile)
    tracker.log_upload_completion(remote_name)

    print("\n" + "="*60)
    print("🎉 OpenSSL Package Upload Summary")
    print("="*60)
    print(f"📦 Package: {mock_conanfile.name}/{mock_conanfile.version}")
    print(f"📤 Remote: {remote_name or 'default'}")
    print(f"🖥️  Platform: {mock_conanfile.settings.os}-{mock_conanfile.settings.arch}")
    print(f"🏗️  Build: {mock_conanfile.settings.build_type}")
    print(f"🔐 FIPS: {'Enabled' if mock_conanfile.options.fips else 'Disabled'}")
    print("="*60)

if __name__ == "__main__":
    main()