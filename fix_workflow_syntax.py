#!/usr/bin/env python3
"""
Fix workflow syntax issues
"""

import os
import re
from pathlib import Path

def fix_workflow_file(file_path):
    """Fix common syntax issues in workflow files"""
    print(f"Fixing {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix incomplete python-version
    content = re.sub(r"python-version: '3\.\n", "python-version: '3.12'\n", content)
    
    # Fix malformed cache lines
    content = re.sub(r"cache: \\'pip\\'1\n", "cache: 'pip'\n", content)
    
    # Fix duplicate cache lines
    content = re.sub(r"cache: 'pip'\n\s*cache: 'pip'\n", "cache: 'pip'\n", content)
    
    # Fix malformed run steps
    content = re.sub(r"-\s*run: pip install", "      - name: Install Conan\n        run: pip install", content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"  ✓ Fixed {file_path}")

def main():
    """Fix all workflow files"""
    workflow_dir = Path(".github/workflows")
    
    if not workflow_dir.exists():
        print("No .github/workflows directory found")
        return
    
    workflow_files = list(workflow_dir.glob("*.yml"))
    print(f"Found {len(workflow_files)} workflow files")
    
    fixed_count = 0
    for workflow_file in workflow_files:
        try:
            fix_workflow_file(workflow_file)
            fixed_count += 1
        except Exception as e:
            print(f"  ✗ Error fixing {workflow_file}: {e}")
    
    print(f"\nFixed {fixed_count}/{len(workflow_files)} workflow files")

if __name__ == "__main__":
    main()