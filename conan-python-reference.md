# Conan Python Reference Guide

## Table of Contents
1. [Conan 2.x Fundamentals](#conan-2x-fundamentals)
2. [Python Integration](#python-integration)
3. [Package Development](#package-development)
4. [Dependency Management](#dependency-management)
5. [Build Systems](#build-systems)
6. [CI/CD Integration](#cicd-integration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Conan 2.x Fundamentals

### Core Concepts
- **Conanfile**: Python script defining package behavior
- **Profiles**: Build configuration (compiler, OS, architecture)
- **Remotes**: Package repositories (ConanCenter, Artifactory, etc.)
- **Lockfiles**: Reproducible dependency resolution
- **Generators**: Build system integration (CMake, Make, etc.)

### Key Changes from Conan 1.x
- New `conan.tools` modules
- Simplified API
- Better Python integration
- Improved dependency resolution
- Enhanced lockfile support

## Python Integration

### Basic Conanfile Structure
```python
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get, save
import os

class MyPackageConan(ConanFile):
    # Package metadata
    name = "mypackage"
    version = "1.0.0"
    description = "My awesome package"
    license = "MIT"
    author = "Your Name <your.email@example.com>"
    url = "https://github.com/yourusername/mypackage"
    homepage = "https://github.com/yourusername/mypackage"
    
    # Package settings
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_tests": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_tests": False,
    }
    
    # Dependencies
    def requirements(self):
        self.requires("fmt/10.1.1")
        self.requires("spdlog/1.12.0")
    
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.15]")
        if self.options.enable_tests:
            self.tool_requires("gtest/1.14.0")
    
    # Configuration
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    # Package ID optimization
    def package_id(self):
        # Remove options that don't affect the binary
        del self.info.options.enable_tests
    
    # Source code management
    def source(self):
        get(self, "https://github.com/yourusername/mypackage/archive/v1.0.0.tar.gz",
            destination=self.source_folder, strip_root=True)
    
    # Build system generation
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TESTS"] = self.options.enable_tests
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()
    
    # Build process
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        
        if self.options.enable_tests:
            cmake.test()
    
    # Package creation
    def package(self):
        cmake = CMake(self)
        cmake.install()
        
        # Copy additional files
        copy(self, "*.h", src=self.source_folder, 
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", src=self.source_folder, 
             dst=os.path.join(self.package_folder, "licenses"))
    
    # Package information
    def package_info(self):
        self.cpp_info.libs = ["mypackage"]
        self.cpp_info.defines = ["MYPACKAGE_VERSION=1.0.0"]
        
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
```

## Package Development

### Header-Only Libraries
```python
from conan import ConanFile
from conan.tools.files import copy
import os

class HeaderOnlyConan(ConanFile):
    name = "headeronly"
    version = "1.0.0"
    description = "Header-only library"
    
    # No settings needed for header-only
    no_copy_source = True
    
    def package_id(self):
        self.info.clear()
    
    def package(self):
        copy(self, "*.h", src=self.source_folder, 
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp", src=self.source_folder, 
             dst=os.path.join(self.package_folder, "include"))
    
    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
```

### Python Extensions
```python
from conan import ConanFile
from conan.tools.python import PythonToolchain, PythonDeps
from conan.tools.files import copy
import os

class PythonExtensionConan(ConanFile):
    name = "python_extension"
    version = "1.0.0"
    description = "Python C++ extension"
    
    settings = "os", "arch", "compiler", "build_type"
    generators = "PythonToolchain", "PythonDeps"
    
    def requirements(self):
        self.requires("pybind11/2.11.1")
    
    def build_requirements(self):
        self.tool_requires("python/[>=3.8]")
    
    def generate(self):
        tc = PythonToolchain(self)
        tc.generate()
        
        deps = PythonDeps(self)
        deps.generate()
    
    def build(self):
        # Build Python extension
        import subprocess
        subprocess.run(["python", "setup.py", "build_ext", "--inplace"])
    
    def package(self):
        copy(self, "*.py", src=self.source_folder, 
             dst=os.path.join(self.package_folder, "python"))
        copy(self, "*.so", src=self.build_folder, 
             dst=os.path.join(self.package_folder, "python"))
        copy(self, "*.pyd", src=self.build_folder, 
             dst=os.path.join(self.package_folder, "python"))
    
    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
```

## Dependency Management

### Version Ranges and Constraints
```python
def requirements(self):
    # Exact version
    self.requires("fmt/10.1.1")
    
    # Version range
    self.requires("spdlog/[>=1.12.0]")
    
    # Multiple constraints
    self.requires("boost/[>=1.80.0,<2.0.0]")
    
    # Optional dependencies
    if self.options.enable_graphics:
        self.requires("opengl/system")
```

### Conditional Dependencies
```python
def requirements(self):
    if self.settings.os == "Linux":
        self.requires("libudev/system")
    elif self.settings.os == "Windows":
        self.requires("directx/system")
    elif self.settings.os == "Macos":
        self.requires("corefoundation/system")
```

### Build Requirements
```python
def build_requirements(self):
    # Always required
    self.tool_requires("cmake/[>=3.15]")
    
    # Conditional build requirements
    if self.settings.compiler == "gcc":
        self.tool_requires("gcc/[>=9.0]")
    elif self.settings.compiler == "clang":
        self.tool_requires("clang/[>=12.0]")
```

## Build Systems

### CMake Integration
```python
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

def generate(self):
    tc = CMakeToolchain(self)
    
    # Set CMake variables
    tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
    tc.variables["ENABLE_TESTS"] = self.options.enable_tests
    
    # Set generator
    if self.settings.os == "Windows":
        tc.generator = "Visual Studio 17 2022"
    else:
        tc.generator = "Ninja"
    
    tc.generate()
    
    deps = CMakeDeps(self)
    deps.generate()

def build(self):
    cmake = CMake(self)
    cmake.configure()
    cmake.build()
    
    if self.options.enable_tests:
        cmake.test()
```

### Make Integration
```python
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools

def generate(self):
    tc = AutotoolsToolchain(self)
    tc.configure_args = ["--enable-shared" if self.options.shared else "--disable-shared"]
    tc.generate()
    
    deps = AutotoolsDeps(self)
    deps.generate()

def build(self):
    autotools = Autotools(self)
    autotools.configure()
    autotools.make()
```

### Meson Integration
```python
from conan.tools.meson import MesonToolchain, MesonDeps, Meson

def generate(self):
    tc = MesonToolchain(self)
    tc.project_options["default_library"] = "shared" if self.options.shared else "static"
    tc.generate()
    
    deps = MesonDeps(self)
    deps.generate()

def build(self):
    meson = Meson(self)
    meson.configure()
    meson.build()
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Conan CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
          - profile: linux-gcc11
          - profile: linux-clang15
          - profile: windows-vs2022
          - profile: macos-clang14
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install Conan
      run: pip install conan
    
    - name: Create profile
      run: conan profile detect --force
    
    - name: Install dependencies
      run: conan install . --profile=${{ matrix.profile }} --build=missing
    
    - name: Build package
      run: conan create . --profile=${{ matrix.profile }} --build=missing
    
    - name: Test package
      run: conan test test_package mypackage/1.0.0@user/channel --profile=${{ matrix.profile }}
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    
    stages {
        stage('Install Conan') {
            steps {
                sh 'pip install conan'
            }
        }
        
        stage('Create Profile') {
            steps {
                sh 'conan profile detect --force'
            }
        }
        
        stage('Build Package') {
            steps {
                sh 'conan create . --build=missing'
            }
        }
        
        stage('Test Package') {
            steps {
                sh 'conan test test_package mypackage/1.0.0@user/channel'
            }
        }
    }
}
```

## Best Practices

### Package ID Optimization
```python
def package_id(self):
    # Remove options that don't affect the binary
    del self.info.options.enable_tests
    del self.info.options.enable_docs
    
    # Group compatible configurations
    if self.settings.compiler == "gcc":
        if self.settings.compiler.version in ["9", "10", "11"]:
            self.info.settings.compiler.version = "9-11"
```

### Error Handling
```python
def build(self):
    try:
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    except Exception as e:
        self.output.error(f"Build failed: {e}")
        raise
```

### Logging and Debugging
```python
def build(self):
    self.output.info(f"Building with compiler: {self.settings.compiler}")
    self.output.info(f"Build type: {self.settings.build_type}")
    
    if self.options.shared:
        self.output.info("Building shared library")
    else:
        self.output.info("Building static library")
```

### Cross-Compilation
```python
def generate(self):
    tc = CMakeToolchain(self)
    
    # Cross-compilation settings
    if self.settings.os == "Linux" and self.settings.arch == "armv8":
        tc.variables["CMAKE_SYSTEM_NAME"] = "Linux"
        tc.variables["CMAKE_SYSTEM_PROCESSOR"] = "aarch64"
    
    tc.generate()
```

## Troubleshooting

### Common Issues

#### Package Not Found
```bash
# Check available packages
conan search "*" -r=all

# Check remote configuration
conan remote list

# Add ConanCenter if missing
conan remote add conancenter https://center.conan.io
```

#### Build Failures
```bash
# Clean cache
conan remove "*" --force

# Rebuild from source
conan create . --build=missing

# Verbose output
conan create . --build=missing -v
```

#### Dependency Conflicts
```bash
# Check dependency graph
conan graph info . --format=json

# Use lockfile for reproducible builds
conan lock create conanfile.py --lockfile=conan.lock
```

### Debugging Tips

1. **Use verbose output**: Add `-v` flag to commands
2. **Check package info**: Use `conan info .` to see dependency information
3. **Inspect generated files**: Check `build/` and `package/` directories
4. **Use lockfiles**: For reproducible builds and debugging dependency issues
5. **Profile analysis**: Use `conan graph info` to understand dependency relationships

### Performance Optimization

1. **Package ID optimization**: Remove non-binary-affecting options
2. **Binary caching**: Use remotes for binary packages
3. **Parallel builds**: Use `-j` flag for parallel compilation
4. **Incremental builds**: Use `--build=missing` to avoid unnecessary rebuilds

This reference guide provides comprehensive coverage of Conan Python integration. Use it as a starting point and adapt the examples to your specific needs.