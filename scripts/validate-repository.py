#!/usr/bin/env python3
"""
Basic validation script for OpenSSL repository
Handles complex validation logic moved from YAML workflow
"""

import os
import sys
import yaml
import importlib.util
from pathlib import Path


def validate_conanfiles():
    """Validate conanfile syntax and basic functionality"""
    print("🔍 Validating conanfile syntax...")
    
    # Test main conanfile.py
    try:
        import py_compile
        py_compile.compile('conanfile.py', doraise=True)
        print("✅ conanfile.py syntax valid")
        
        # Test basic functionality
        sys.path.append('.')
        from conanfile import OpenSSLConan
        
        conan = OpenSSLConan()
        conan.recipe_folder = '.'
        conan.set_version()
        print(f"✅ Version detection works: {conan.version}")
        
        conan.configure()
        print("✅ Basic configuration works")
        
    except Exception as e:
        print(f"❌ conanfile.py validation failed: {e}")
        return False
    
    return True


def validate_yaml_files():
    """Validate all YAML files in repository"""
    print("🔍 Validating YAML files...")
    
    yaml_files = list(Path('.').rglob('*.yml')) + list(Path('.').rglob('*.yaml'))
    
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r') as f:
                yaml.safe_load(f)
            print(f"✅ {yaml_file} is valid YAML")
        except yaml.YAMLError as e:
            print(f"❌ {yaml_file} has YAML error: {e}")
            return False
        except Exception as e:
            print(f"⚠️  Could not read {yaml_file}: {e}")
    
    return True


def validate_version_dat():
    """Validate VERSION.dat file"""
    print("🔍 Validating VERSION.dat...")
    
    if not Path("VERSION.dat").exists():
        print("❌ VERSION.dat not found")
        return False
    
    try:
        with open("VERSION.dat", 'r') as f:
            content = f.read()
        
        required_fields = ["MAJOR=", "MINOR=", "PATCH="]
        for field in required_fields:
            if field not in content:
                print(f"❌ VERSION.dat missing {field}")
                return False
        
        print("✅ VERSION.dat is valid")
        return True
        
    except Exception as e:
        print(f"❌ Failed to read VERSION.dat: {e}")
        return False


def validate_repository_structure():
    """Validate minimal repository structure"""
    print("🔍 Validating repository structure...")
    
    required_files = [
        "conanfile.py",
        "VERSION.dat",
        "Configure",
        "config",
        ".github/workflows/trigger-tools.yml",
        ".github/workflows/basic-validation.yml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ Missing: {file_path}")
        else:
            print(f"✅ Found: {file_path}")
    
    if missing_files:
        print(f"❌ Repository structure validation failed - missing {len(missing_files)} files")
        return False
    
    print("✅ Repository structure validation passed")
    return True


def main():
    """Run all validations"""
    print("🚀 Starting OpenSSL repository validation...")
    
    validations = [
        ("VERSION.dat", validate_version_dat),
        ("YAML files", validate_yaml_files),  
        ("Conanfiles", validate_conanfiles),
        ("Repository structure", validate_repository_structure),
    ]
    
    results = []
    for name, validation_func in validations:
        print(f"\n--- {name} ---")
        try:
            result = validation_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} validation crashed: {e}")
            results.append((name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("VALIDATION SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / len(results)) * 100
    print(f"\nOverall: {passed}/{len(results)} validations passed ({success_rate:.1f}%)")
    
    if passed == len(results):
        print("🎉 All validations passed!")
        sys.exit(0)
    else:
        print("💥 Some validations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()