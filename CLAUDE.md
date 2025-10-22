# OpenSSL - Cryptographic Library Package

## 📦 Package Overview
- **Name**: `openssl`
- **Version**: `4.0.2` (current)
- **Channel**: `stable`
- **User**: `sparesparrow`
- **Purpose**: OpenSSL cryptographic library with layered architecture support

## 🔄 Version Management Rules

### Before Making Changes
1. **ALWAYS update version first** in `conanfile.py`
2. **NEVER modify conanfile.py** without version bump
3. **Update dependency versions** if foundation/tooling packages changed
4. **Commit version change** before calling `conan create`

### Version Update Workflow
```bash
# 1. Update version in conanfile.py
version = "4.0.3"  # Increment appropriately

# 2. Update dependency versions if needed
requires = [
    "openssl-base/1.0.2@sparesparrow/stable",
    "openssl-tools/1.2.5@sparesparrow/stable",
    "openssl-fips-data/140-3.3@sparesparrow/stable"
]

# 3. Commit the change
git add conanfile.py
git commit -m "bump: openssl to 4.0.3"

# 4. Build and upload
conan create . --build=missing
conan upload openssl/4.0.3@sparesparrow/stable -r=sparesparrow-conan
```

## 📋 Package Contents

### Exported Sources
- All OpenSSL source files (crypto/, ssl/, apps/, test/, etc.)
- Build configuration files (Configure, config*, Makefile*)
- Documentation and license files

### Package Artifacts
- **Libraries**: `lib/` directory with `*.so*` and `*.a` files
- **Headers**: `include/` directory with `*.h` files
- **Binaries**: `bin/` directory with `openssl` executable
- **Licenses**: `licenses/` directory with `LICENSE.txt`

### CMake Integration
- `cmake_file_name`: "OpenSSL"
- `cmake_target_name`: "OpenSSL::OpenSSL"
- `libs`: ["ssl", "crypto"]
- System dependencies for Linux, Windows, macOS

### Environment Variables
- `PATH` - Prepend bin directory for openssl executable

## 🏗️ Build Process

### Dependencies
- `openssl-base/1.0.1@sparesparrow/stable` - Foundation utilities
- `openssl-tools/1.2.4@sparesparrow/stable` - Build orchestration
- `openssl-fips-data/140-3.2@sparesparrow/stable` - FIPS compliance data

### Build Commands
```bash
# Install dependencies (will use cached packages)
conan install . --build=missing

# Create package (this builds the full OpenSSL library)
conan create . --build=missing

# Upload to remote
conan upload openssl/4.0.2@sparesparrow/stable -r=sparesparrow-conan
```

### Build System
- **Traditional Configure/Make**: Uses OpenSSL's native build system
- **Platform Support**: Linux, Windows, macOS
- **Options**: shared/static, fPIC support
- **Staging Install**: Uses DESTDIR for clean packaging

## 🧪 Validation

### Package Validation
```bash
# Check package contents
conan cache path openssl/4.0.2@sparesparrow/stable

# Validate with script
python ../scripts/validate-conan-packages.py openssl/4.0.2
```

### Expected Contents
- ✅ `lib/` directory with ssl and crypto libraries
- ✅ `include/` directory with OpenSSL headers
- ✅ `bin/` directory with openssl executable
- ✅ `licenses/` directory with LICENSE.txt
- ✅ CMake integration properties set
- ✅ Environment variables properly set
- ✅ Dependencies correctly resolved

## 🔗 Dependencies

### Requires
- `openssl-base` - Foundation utilities and profiles
- `openssl-tools` - Build orchestration tools
- `openssl-fips-data` - FIPS compliance data

### Consumed By
- Applications using OpenSSL
- Other cryptographic libraries
- Test projects and examples

### Version Compatibility
- **Major version changes** (3.x → 4.x): Breaking changes, update all consumers
- **Minor version changes** (4.0.x → 4.1.x): New features, backward compatible
- **Patch version changes** (4.0.1 → 4.0.2): Bug fixes, fully backward compatible

## 🚨 Critical Notes

1. **Domain Layer**: Top of the dependency chain
2. **Full Build**: Compiles the complete OpenSSL library
3. **Dependency Chain**: Must update when any dependency changes
4. **CMake Integration**: Provides proper CMake targets
5. **Multi-Platform**: Supports Linux, Windows, macOS

## 📝 Change Log

### Version 4.0.2
- Added openssl-fips-data dependency
- Updated all dependency versions to latest
- Fixed package() method for proper staging install
- Enhanced package_info() for CMake integration

### Version 4.0.1
- Initial release with layered architecture support
- Traditional Configure/Make build system
- CMake integration properties


**Role:** 🟡 Domain Layer (Source code)

Main OpenSSL cryptographic library with Conan 2.x packaging and FIPS support

## Architecture Position

**Layer:** Domain (Top of dependency hierarchy)
**Dependencies:**
- openssl-base/1.0.1 (python_requires)
- openssl-tools/1.2.4 (python_requires)
- openssl-fips-data/140-3.2 (python_requires)
**Consumers:** Downstream applications (curl, etc.)

## Key Files

- `conanfile.py`: Main package (v4.0.3)
- `crypto/`, `ssl/`: Core cryptographic implementations
- `providers/fips/`: FIPS provider module
- `test/`: Comprehensive test suite
- `BUILDING-CONAN.md`: Conan integration documentation

## Quick Start

```bash
# Clone repository (if not in workspace)
git clone https://github.com/sparesparrow/openssl.git

# Navigate to directory
cd openssl

# Create Conan package
conan create . --build=missing
```

## Related Documentation

- [Main Architecture Diagram](../architecture-diagram.md)
- [Workspace Overview](../README.md)
- [Conan Integration Guide](../docs/conan-extensions-diagram.md)

---
