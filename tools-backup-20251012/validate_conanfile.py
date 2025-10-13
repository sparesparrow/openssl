#!/usr/bin/env python3
import sys
from pathlib import Path

def validate_conanfile():
    """Validate conanfile.py basic functionality"""
    try:
        sys.path.append('.')
        from conanfile import OpenSSLConan
        
        conan = OpenSSLConan()
        conan.recipe_folder = '.'
        
        # Test version detection
        conan.set_version()
        print(f'✅ Version detection works: {conan.version}')
        
        # Test basic attributes
        assert hasattr(conan, 'name')
        assert hasattr(conan, 'version')
        assert hasattr(conan, 'options')
        assert hasattr(conan, 'settings')
        print('✅ Basic class structure is valid')
        
        return 0
    except Exception as e:
        print(f'❌ Validation failed: {e}')
        return 1

if __name__ == '__main__':
    sys.exit(validate_conanfile())
