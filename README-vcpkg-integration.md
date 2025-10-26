# OpenSSL Tools vcpkg Integration

This document describes the vcpkg integration features added to the OpenSSL tools package.

## Overview

The `openssl-tools` package now includes comprehensive vcpkg integration, allowing you to use vcpkg as an alternative package manager for OpenSSL dependencies. This integration provides:

- Automatic vcpkg detection and setup
- CMake integration with vcpkg toolchain
- Conan integration with vcpkg packages
- Project templates with vcpkg support
- FIPS 140-3 compliance support

## Features

### 🔍 Automatic Detection
- Detects vcpkg installation from common locations
- Supports environment variables (`VCPKG_ROOT`, `VCPKG_INSTALLATION_ROOT`)
- Validates vcpkg installation and functionality

### 🏗️ Build Integration
- CMake toolchain file generation
- Automatic triplet detection based on platform
- Environment variable setup for vcpkg integration

### 📦 Package Management
- Install OpenSSL and dependencies via vcpkg
- Support for FIPS 140-3 features
- Package search and validation

### 🎯 Project Templates
- Complete project templates with vcpkg integration
- CMakeLists.txt with OpenSSL linking
- vcpkg.json manifest generation
- Environment setup scripts

## Installation

### Prerequisites
- Python 3.7+
- vcpkg (optional, will be auto-detected)
- CMake 3.20+

### Install vcpkg (if not already installed)
```bash
# Clone vcpkg
git clone https://github.com/Microsoft/vcpkg.git ~/vcpkg

# Bootstrap vcpkg
cd ~/vcpkg
./bootstrap-vcpkg.sh

# Set environment variable
export VCPKG_ROOT=~/vcpkg
```

### Install OpenSSL Tools
```bash
# Install via Conan
conan create openssl-tools-conanfile.py --build=missing

# Or install Python package directly
pip install -e .
```

## Usage

### Basic Usage

```python
from openssl_tools.vcpkg import VcpkgIntegration, VcpkgManager
from openssl_tools.build import OpenSSLBuildManager

# Create vcpkg integration
integration = VcpkgIntegration()

# Check if vcpkg is available
if integration.detector.is_vcpkg_available():
    print("vcpkg is available!")
    
    # Install OpenSSL dependencies
    manager = VcpkgManager()
    success = manager.install_openssl_dependencies(fips_mode=False)
    
    if success:
        print("OpenSSL installed via vcpkg")
```

### CMake Integration

```cmake
# Include vcpkg integration
include(vcpkg-openssl.cmake)

# Find OpenSSL
find_package(OpenSSL REQUIRED)

# Link with OpenSSL
target_link_libraries(your_target 
    PRIVATE 
    OpenSSL::SSL 
    OpenSSL::Crypto
)
```

### Conan Integration

```python
from conan import ConanFile
from openssl_tools.vcpkg import VcpkgIntegration

class YourConanFile(ConanFile):
    def configure(self):
        # Enable vcpkg integration
        self.options.vcpkg_integration = True
        self.options.prefer_vcpkg = True
    
    def generate(self):
        # Setup vcpkg integration
        integration = VcpkgIntegration()
        env_vars = integration.setup_environment()
        
        # Set environment variables
        for key, value in env_vars.items():
            self.env_info.define(key, value)
```

### Project Template

```python
from openssl_tools.vcpkg import VcpkgIntegration

# Create a new project with vcpkg integration
integration = VcpkgIntegration()
success = integration.create_project_template(
    project_dir="my-openssl-project",
    project_name="my-openssl-project"
)

if success:
    print("Project created with vcpkg integration!")
```

## Configuration Options

### Conan Options

```python
options = {
    "vcpkg_integration": [True, False],  # Enable vcpkg integration
    "fips_mode": [True, False],          # Enable FIPS 140-3 features
    "prefer_vcpkg": [True, False]        # Prefer vcpkg over Conan packages
}
```

### Environment Variables

- `VCPKG_ROOT`: Path to vcpkg installation
- `VCPKG_DEFAULT_TRIPLET`: Default vcpkg triplet
- `CMAKE_TOOLCHAIN_FILE`: Path to vcpkg CMake toolchain file

## File Structure

```
openssl-tools/
├── conanfile.py                    # Main Conan package file
├── openssl_tools/
│   ├── __init__.py
│   ├── vcpkg/
│   │   ├── __init__.py
│   │   ├── detector.py            # vcpkg detection utilities
│   │   ├── manager.py             # Package management
│   │   └── integration.py         # Integration utilities
│   └── build.py                   # Build management
├── vcpkg/
│   ├── manifests/
│   │   └── vcpkg.json             # vcpkg manifest
│   ├── scripts/
│   │   └── setup-vcpkg.sh         # Setup script
│   └── templates/
│       ├── CMakeLists.txt         # CMake template
│       └── main.cpp               # C++ template
└── test_vcpkg_integration.py      # Test script
```

## Testing

Run the test suite to validate vcpkg integration:

```bash
python test_vcpkg_integration.py
```

This will test:
- vcpkg detection
- Package management
- CMake integration
- Project template creation
- Conan integration

## Troubleshooting

### vcpkg Not Found
```bash
# Check if vcpkg is installed
ls ~/vcpkg/vcpkg

# Set VCPKG_ROOT environment variable
export VCPKG_ROOT=~/vcpkg
```

### CMake Integration Issues
```bash
# Verify CMake toolchain file exists
ls $VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake

# Check environment variables
echo $CMAKE_TOOLCHAIN_FILE
```

### Package Installation Issues
```bash
# Update vcpkg
cd $VCPKG_ROOT
git pull
./bootstrap-vcpkg.sh

# Install OpenSSL
./vcpkg install openssl[core,tools]
```

## Examples

### Example 1: Basic vcpkg Integration

```python
from openssl_tools.vcpkg import VcpkgIntegration

# Create integration
integration = VcpkgIntegration()

# Check status
validation = integration.validate_integration()
print(f"vcpkg available: {validation['vcpkg_available']}")
print(f"OpenSSL installed: {validation['openssl_installed']}")

# Setup environment
env_vars = integration.setup_environment("setup-env.sh")
print(f"Environment variables: {list(env_vars.keys())}")
```

### Example 2: CMake Project with vcpkg

```cmake
cmake_minimum_required(VERSION 3.20)
project(MyOpenSSLProject)

# Include vcpkg integration
include(vcpkg-openssl.cmake)

# Add executable
add_executable(myapp main.cpp)

# Link with OpenSSL
target_link_libraries(myapp PRIVATE OpenSSL::SSL OpenSSL::Crypto)
```

### Example 3: Conan Package with vcpkg

```python
from conan import ConanFile
from openssl_tools.vcpkg import VcpkgIntegration

class MyConanFile(ConanFile):
    options = {
        "use_vcpkg": [True, False]
    }
    default_options = {
        "use_vcpkg": True
    }
    
    def configure(self):
        if self.options.use_vcpkg:
            integration = VcpkgIntegration()
            if integration.detector.is_vcpkg_available():
                self.output.info("Using vcpkg for dependencies")
            else:
                self.output.warning("vcpkg not available, using Conan packages")
```

## Contributing

To contribute to the vcpkg integration:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the Apache-2.0 License. See the LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the test script for examples