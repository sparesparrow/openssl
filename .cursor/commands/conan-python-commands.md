# Cursor Commands for Conan Python Development

## Package Creation Commands

### `@conan-create-basic`
Creates a basic conanfile.py template with essential structure:
```python
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class MyPackageConan(ConanFile):
    name = "mypackage"
    version = "1.0.0"
    description = "Package description"
    license = "MIT"
    
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    
    def requirements(self):
        # Add dependencies here
        pass
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        cmake = CMake(self)
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = ["mypackage"]
```

### `@conan-create-header-only`
Creates a header-only library conanfile.py:
```python
from conan import ConanFile
from conan.tools.files import copy

class HeaderOnlyConan(ConanFile):
    name = "headeronly"
    version = "1.0.0"
    description = "Header-only library"
    
    # No settings needed for header-only
    no_copy_source = True
    
    def package_id(self):
        self.info.clear()
    
    def package(self):
        copy(self, "*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
    
    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
```

### `@conan-create-python`
Creates a Python package conanfile.py:
```python
from conan import ConanFile
from conan.tools.python import PythonToolchain, PythonDeps
from conan.tools.files import copy

class PythonPackageConan(ConanFile):
    name = "pythonpackage"
    version = "1.0.0"
    description = "Python package"
    
    settings = "os", "arch", "compiler", "build_type"
    generators = "PythonToolchain", "PythonDeps"
    
    def requirements(self):
        self.requires("pybind11/2.11.1")
    
    def build_requirements(self):
        self.tool_requires("python/[>=3.8]")
    
    def build(self):
        # Build Python extension
        pass
    
    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=os.path.join(self.package_folder, "python"))
        copy(self, "*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "python"))
```

## Test Package Commands

### `@conan-test-basic`
Creates a basic test_package structure:
```python
import os
from conan import ConanFile
from conan.tools.cmake import CMake

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    test_type = "explicit"
    
    def requirements(self):
        self.requires(self.tested_reference_str)
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def test(self):
        self.run(os.path.join(".", "test_package"))
```

### `@conan-test-python`
Creates a Python test package:
```python
from conan import ConanFile
from conan.tools.python import PythonToolchain, PythonDeps

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "PythonToolchain", "PythonDeps"
    test_type = "explicit"
    
    def requirements(self):
        self.requires(self.tested_reference_str)
    
    def test(self):
        # Test Python package
        import mypackage
        assert mypackage.version() == "1.0.0"
```

## Profile Commands

### `@conan-profile-linux-gcc`
Creates a Linux GCC profile:
```ini
[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Ninja
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True
```

### `@conan-profile-windows-msvc`
Creates a Windows MSVC profile:
```ini
[settings]
os=Windows
arch=x86_64
compiler=msvc
compiler.version=193
compiler.runtime=dynamic
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Visual Studio 17 2022
```

### `@conan-profile-macos-clang`
Creates a macOS Clang profile:
```ini
[settings]
os=Macos
arch=x86_64
compiler=apple-clang
compiler.version=14
compiler.libcxx=libc++
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Xcode
```

## Build Commands

### `@conan-build-debug`
Creates debug build configuration:
```bash
conan create . --profile=debug --build=missing
```

### `@conan-build-release`
Creates release build configuration:
```bash
conan create . --profile=release --build=missing
```

### `@conan-build-cross`
Creates cross-compilation build:
```bash
conan create . --profile:host=linux-gcc --profile:build=linux-gcc --build=missing
```

## Dependency Management Commands

### `@conan-lockfile-generate`
Generates lockfile for dependencies:
```bash
conan lock create conanfile.py --lockfile=conan.lock
```

### `@conan-graph-info`
Shows dependency graph information:
```bash
conan graph info . --format=json
```

### `@conan-export-pkg`
Exports package to local cache:
```bash
conan export-pkg . mypackage/1.0.0@user/channel
```

## CI/CD Commands

### `@conan-ci-setup`
Sets up CI/CD environment:
```bash
# Install Conan
pip install conan

# Create profile
conan profile detect --force

# Install dependencies
conan install . --build=missing

# Build package
conan create . --build=missing
```

### `@conan-ci-test`
Runs CI/CD tests:
```bash
conan test test_package mypackage/1.0.0@user/channel
```

## Package Management Commands

### `@conan-upload`
Uploads package to remote:
```bash
conan upload mypackage/1.0.0@user/channel -r=myremote --all
```

### `@conan-search`
Searches for packages:
```bash
conan search "*" -r=all
```

### `@conan-remove`
Removes package from cache:
```bash
conan remove mypackage/1.0.0@user/channel --force
```

## Development Commands

### `@conan-dev-install`
Installs package in development mode:
```bash
conan install . --build=missing
```

### `@conan-dev-build`
Builds package in development mode:
```bash
conan build .
```

### `@conan-dev-test`
Tests package in development mode:
```bash
conan test test_package .
```

## Utility Commands

### `@conan-clean`
Cleans Conan cache:
```bash
conan remove "*" --force
```

### `@conan-info`
Shows package information:
```bash
conan info .
```

### `@conan-config`
Configures Conan settings:
```bash
conan config install https://github.com/conan-io/conan-config.git
```

## Advanced Commands

### `@conan-multi-config`
Creates multi-configuration build:
```bash
conan create . --profile:host=linux-gcc --profile:build=linux-gcc --build=missing -s build_type=Release
conan create . --profile:host=linux-gcc --profile:build=linux-gcc --build=missing -s build_type=Debug
```

### `@conan-cross-compile`
Sets up cross-compilation:
```bash
conan create . --profile:host=arm-linux-gcc --profile:build=linux-gcc --build=missing
```

### `@conan-docker`
Creates Docker-based build:
```dockerfile
FROM conanio/gcc11:latest
COPY . /app
WORKDIR /app
RUN conan create . --build=missing
```

## Best Practices Commands

### `@conan-best-practices`
Applies best practices to conanfile.py:
- Adds proper package_id() method
- Implements config_options() and configure()
- Adds comprehensive package_info()
- Includes proper error handling
- Adds version validation

### `@conan-security`
Applies security best practices:
- Validates package signatures
- Checks for known vulnerabilities
- Implements secure defaults
- Adds security scanning

### `@conan-performance`
Applies performance optimizations:
- Enables parallel builds
- Optimizes package ID generation
- Implements intelligent caching
- Adds performance monitoring

Remember: These commands are designed to work with Cursor's AI capabilities. Use them as starting points and let Cursor's AI help you customize them for your specific needs.