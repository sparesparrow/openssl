#!/usr/bin/env python3
"""
OpenSSL File Copy Utility - Python replacement for copy.pl

Copies files with special handling for timestamps, CR stripping, and exclusions.
"""

import argparse
import glob
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List


class FileCopier:
    """Handles file copying with OpenSSL-specific options."""

    def __init__(self):
        self.strip_cr = False
        self.excludes: List[str] = []
        self.verbose = False

    def should_exclude(self, filename: str) -> bool:
        """Check if file should be excluded based on patterns."""
        for pattern in self.excludes:
            if re.search(pattern, filename):
                return True
        return False

    def strip_carriage_returns(self, content: bytes) -> bytes:
        """Strip carriage return characters from content."""
        return content.replace(b'\r\n', b'\n').replace(b'\r', b'\n')

    def copy_file(self, src: str, dst: str) -> None:
        """Copy a single file with appropriate handling."""
        if self.verbose:
            print(f"Copying {src} -> {dst}")

        # Ensure destination directory exists
        dst_path = Path(dst)
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        if self.strip_cr:
            # Read, strip CR, write
            with open(src, 'rb') as f:
                content = f.read()

            content = self.strip_carriage_returns(content)

            with open(dst, 'wb') as f:
                f.write(content)
        else:
            # Simple copy
            shutil.copy2(src, dst)

    def expand_patterns(self, patterns: List[str]) -> List[str]:
        """Expand glob patterns and apply exclusions."""
        files = []

        for pattern in patterns:
            # Convert backslashes to forward slashes for glob compatibility
            pattern = pattern.replace('\\', '/')

            # Handle quoted arguments with spaces
            if pattern.startswith('"') and pattern.endswith('"'):
                pattern = pattern[1:-1]

            # Expand glob patterns
            try:
                expanded = glob.glob(pattern)
                for f in expanded:
                    if not self.should_exclude(f):
                        files.append(f)
            except Exception as e:
                print(f"Warning: Failed to expand pattern '{pattern}': {e}", file=sys.stderr)

        return files

    def run(self, args: List[str]) -> int:
        """Main execution method."""
        parser = argparse.ArgumentParser(description='Copy files with OpenSSL-specific handling')
        parser.add_argument('-stripcr', action='store_true',
                          help='Strip carriage return characters')
        parser.add_argument('-exclude-re', action='append',
                          help='Exclude files matching regex pattern')
        parser.add_argument('-verbose', '-v', action='store_true',
                          help='Verbose output')
        parser.add_argument('files', nargs='+',
                          help='Source files and destination')

        # Parse known args first to handle special options
        known_args = []
        remaining = args[:]

        i = 0
        while i < len(remaining):
            arg = remaining[i]
            if arg == '-stripcr':
                self.strip_cr = True
                i += 1
            elif arg.startswith('-exclude-re='):
                pattern = arg.split('=', 1)[1]
                self.excludes.append(pattern)
                i += 1
            elif arg == '-verbose' or arg == '-v':
                self.verbose = True
                i += 1
            else:
                known_args.append(arg)
                i += 1

        # Parse with argparse
        try:
            parsed_args = parser.parse_args(known_args)
        except SystemExit:
            return 1

        self.strip_cr = self.strip_cr or parsed_args.stripcr
        if parsed_args.exclude_re:
            self.excludes.extend(parsed_args.exclude_re)
        self.verbose = self.verbose or parsed_args.verbose

        files = parsed_args.files

        if len(files) < 2:
            print("Error: Need at least source and destination files", file=sys.stderr)
            return 1

        # Last argument is destination
        dst = files[-1]
        src_patterns = files[:-1]

        # Expand source patterns
        src_files = self.expand_patterns(src_patterns)

        if not src_files:
            print("Error: No source files found", file=sys.stderr)
            return 1

        if self.verbose:
            print(f"Strip CR: {self.strip_cr}")
            print(f"Excludes: {self.excludes}")
            print(f"Source files: {src_files}")
            print(f"Destination: {dst}")

        # Handle single file vs multiple files
        if len(src_files) == 1 and not dst.endswith('/') and not Path(dst).is_dir():
            # Single file copy
            self.copy_file(src_files[0], dst)
        else:
            # Multiple files to directory
            dst_dir = Path(dst)
            if not dst_dir.is_dir():
                dst_dir.mkdir(parents=True, exist_ok=True)

            for src_file in src_files:
                src_path = Path(src_file)
                dst_file = dst_dir / src_path.name
                self.copy_file(str(src_path), str(dst_file))

        return 0


def main():
    """Main entry point."""
    copier = FileCopier()
    sys.exit(copier.run(sys.argv[1:]))


if __name__ == '__main__':
    main()