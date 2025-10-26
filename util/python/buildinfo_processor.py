#!/usr/bin/env python3
"""
OpenSSL Build Info Processor - Python-based build.info file processor

Processes build.info files to extract build configuration and generate makefiles.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class BuildInfoProcessor:
    """Processes OpenSSL build.info files."""

    def __init__(self):
        self.debug = False
        self.build_info: Dict[str, Dict] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        self.sources: Dict[str, List[str]] = {}
        self.includes: Dict[str, List[str]] = {}
        self.defines: Dict[str, List[str]] = {}

    def parse_build_info_file(self, build_info_path: str) -> None:
        """Parse a build.info file."""
        if not os.path.exists(build_info_path):
            if self.debug:
                print(f"Build info file not found: {build_info_path}")
            return

        current_section = None
        current_program = None

        with open(build_info_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                # Parse section headers
                if line.startswith('[') and line.endswith(']'):
                    section_name = line[1:-1]
                    current_section = section_name

                    if section_name == 'programs':
                        current_program = None
                    elif section_name.startswith('program(') and section_name.endswith(')'):
                        current_program = section_name[8:-1]
                        self.build_info[current_program] = {
                            'type': 'program',
                            'sources': [],
                            'includes': [],
                            'defines': [],
                            'libraries': []
                        }
                    elif section_name.startswith('lib(') and section_name.endswith(')'):
                        lib_name = section_name[4:-1]
                        self.build_info[lib_name] = {
                            'type': 'library',
                            'sources': [],
                            'includes': [],
                            'defines': [],
                            'libraries': []
                        }
                    else:
                        # Generic section
                        self.build_info[section_name] = {
                            'type': 'generic',
                            'sources': [],
                            'includes': [],
                            'defines': [],
                            'libraries': []
                        }

                    continue

                # Parse key-value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle multi-line values (continued with backslash)
                    while value.endswith('\\') and line_num < sum(1 for _ in open(build_info_path)):
                        next_line = next(f).strip()
                        line_num += 1
                        value = value[:-1] + next_line

                    # Process the value
                    if key == 'SOURCES':
                        sources = [s.strip() for s in value.split() if s.strip()]
                        if current_program and current_program in self.build_info:
                            self.build_info[current_program]['sources'].extend(sources)
                        elif current_section and current_section in self.build_info:
                            self.build_info[current_section]['sources'].extend(sources)
                    elif key == 'INCLUDES':
                        includes = [i.strip() for i in value.split() if i.strip()]
                        if current_program and current_program in self.build_info:
                            self.build_info[current_program]['includes'].extend(includes)
                        elif current_section and current_section in self.build_info:
                            self.build_info[current_section]['includes'].extend(includes)
                    elif key == 'DEFINES':
                        defines = [d.strip() for d in value.split() if d.strip()]
                        if current_program and current_program in self.build_info:
                            self.build_info[current_program]['defines'].extend(defines)
                        elif current_section and current_section in self.build_info:
                            self.build_info[current_section]['defines'].extend(defines)
                    elif key == 'LIBRARIES' or key == 'LIBS':
                        libraries = [l.strip() for l in value.split() if l.strip()]
                        if current_program and current_program in self.build_info:
                            self.build_info[current_program]['libraries'].extend(libraries)
                        elif current_section and current_section in self.build_info:
                            self.build_info[current_section]['libraries'].extend(libraries)

    def process_directory(self, directory: str) -> None:
        """Process all build.info files in a directory."""
        build_info_files = []

        # Find all build.info files
        for root, dirs, files in os.walk(directory):
            if 'build.info' in files:
                build_info_files.append(os.path.join(root, 'build.info'))

        # Process each build.info file
        for build_info_file in build_info_files:
            if self.debug:
                print(f"Processing {build_info_file}")
            self.parse_build_info_file(build_info_file)

    def generate_makefile_rules(self, output_file: str) -> None:
        """Generate Makefile rules from parsed build.info data."""
        with open(output_file, 'w') as f:
            f.write("# Generated from build.info files\n")
            f.write("# Do not edit manually\n\n")

            # Generate rules for each component
            for component_name, component_info in self.build_info.items():
                if component_info['type'] == 'library':
                    self._generate_library_rule(f, component_name, component_info)
                elif component_info['type'] == 'program':
                    self._generate_program_rule(f, component_name, component_info)

    def _generate_library_rule(self, f, name: str, info: Dict) -> None:
        """Generate Makefile rule for a library."""
        obj_files = []
        for source in info.get('sources', []):
            if source.endswith('.c'):
                obj_file = source.replace('.c', '.o')
                obj_files.append(obj_file)

        f.write(f"# Library: {name}\n")
        f.write(f"lib{name}.a: {' '.join(obj_files)}\n")
        f.write(f"\t$(AR) $(ARFLAGS) $@ $^\n\n")

        # Compile rules for each source file
        for source in info.get('sources', []):
            if source.endswith('.c'):
                obj_file = source.replace('.c', '.o')
                includes = ' '.join(f'-I{inc}' for inc in info.get('includes', []))
                defines = ' '.join(f'-D{defn}' for defn in info.get('defines', []))
                f.write(f"{obj_file}: {source}\n")
                f.write(f"\t$(CC) $(CFLAGS) {includes} {defines} -c $< -o $@\n")

        f.write("\n")

    def _generate_program_rule(self, f, name: str, info: Dict) -> None:
        """Generate Makefile rule for a program."""
        obj_files = []
        for source in info.get('sources', []):
            if source.endswith('.c'):
                obj_file = source.replace('.c', '.o')
                obj_files.append(obj_file)

        f.write(f"# Program: {name}\n")
        f.write(f"{name}: {' '.join(obj_files)}\n")
        libraries = ' '.join(f'-l{lib}' for lib in info.get('libraries', []))
        f.write(f"\t$(CC) $(LDFLAGS) $^ -o $@ {libraries}\n\n")

        # Compile rules for each source file
        for source in info.get('sources', []):
            if source.endswith('.c'):
                obj_file = source.replace('.c', '.o')
                includes = ' '.join(f'-I{inc}' for inc in info.get('includes', []))
                defines = ' '.join(f'-D{defn}' for defn in info.get('defines', []))
                f.write(f"{obj_file}: {source}\n")
                f.write(f"\t$(CC) $(CFLAGS) {includes} {defines} -c $< -o $@\n")

        f.write("\n")

    def get_component_info(self, component_name: str) -> Optional[Dict]:
        """Get information about a specific component."""
        return self.build_info.get(component_name)

    def get_all_components(self) -> Dict[str, Dict]:
        """Get information about all components."""
        return self.build_info.copy()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Process OpenSSL build.info files')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument('-o', '--output', type=str, help='Output Makefile')
    parser.add_argument('directory', help='Directory containing build.info files')

    args = parser.parse_args()

    processor = BuildInfoProcessor()
    processor.debug = args.debug

    processor.process_directory(args.directory)

    if args.output:
        processor.generate_makefile_rules(args.output)
        print(f"Generated Makefile: {args.output}")
    else:
        # Print component information
        for name, info in processor.get_all_components().items():
            print(f"Component: {name}")
            print(f"  Type: {info.get('type', 'unknown')}")
            print(f"  Sources: {info.get('sources', [])}")
            print(f"  Includes: {info.get('includes', [])}")
            print(f"  Defines: {info.get('defines', [])}")
            print(f"  Libraries: {info.get('libraries', [])}")
            print()


if __name__ == '__main__':
    main()