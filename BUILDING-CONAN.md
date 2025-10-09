# Building OpenSSL with Conan

This document describes how to build OpenSSL using the modern Conan package management system.

## Quick Start

### Prerequisites

1. **Install Conan 2.x**:
   ```bash
   pip install conan
   ```

2. **Verify installation**:
   ```bash
   conan --version
   ```

### Basic Build

```bash
# Clone the repository
git clone https://github.com/sparesparrow/openssl.git
cd openssl

# Create a basic package
conan create . --build=missing

# Or install dependencies only
conan install . --build=missing
```

## Available Profiles

The repository includes several pre-configured profiles in `.conan/profiles/`:

### Production Profiles

- **`linux-gcc-release.profile`** - Production Linux build with GCC
  - Optimized for performance (`-O3 -march=native`)
  - FIPS disabled, shared libraries
  - Tests skipped for faster builds

- **`windows-msvc.profile`** - Production Windows build with MSVC
  - Visual Studio 2022 integration
  - Windows-specific optimizations
  - Platform-specific system libraries

- **`macos-clang.profile`** - Production macOS build with Clang
  - ARM64 optimized
  - macOS deployment target 12.0+
  - Clang-specific optimizations

### Development Profiles

- **`linux-gcc-debug.profile`** - Development Linux build
  - Debug symbols enabled (`-g -O0`)
  - Unit tests enabled
  - Demos and tracing enabled
  - Crypto memory debugging

### FIPS Profiles

- **`linux-fips.profile`** - FIPS-compliant build
  - **CRITICAL**: Separate cache key to prevent contamination
  - FIPS mode enabled with compliance checks
  - Restricted algorithms (no MD2, RC5, RC4, DES)
  - Unit tests enabled for validation

## Usage Examples

### Basic Package Creation

```bash
# Create package with default profile
conan create . --profile=linux-gcc-release

# Create package with specific options
conan create . --profile=linux-gcc-release -o openssl:shared=True -o openssl:fips=False

# Create debug package
conan create . --profile=linux-gcc-debug
```

### FIPS Build

```bash
# Create FIPS-compliant package
conan create . --profile=linux-fips

# Verify FIPS mode
conan create . --profile=linux-fips -o openssl:enable_unit_test=True
```

### Cross-Platform Builds

```bash
# Windows build
conan create . --profile=windows-msvc

# macOS build
conan create . --profile=macos-clang

# Linux with different compiler
conan create . --profile=linux-gcc-release -s compiler=clang -s compiler.version=15
```

### Custom Configuration

```bash
# Custom options
conan create . --profile=linux-gcc-release \
    -o openssl:shared=True \
    -o openssl:enable_quic=True \
    -o openssl:no_deprecated=True \
    -o openssl:enable_demos=False

# Debug with specific features
conan create . --profile=linux-gcc-debug \
    -o openssl:enable_trace=True \
    -o openssl:enable_crypto_mdebug=True \
    -o openssl:enable_unit_test=True
```

## Integration with openssl-tools

The OpenSSL Conan package integrates with the [openssl-tools](https://github.com/sparesparrow/openssl-tools) repository for:

### Artifact Caching
- **Artifactory Integration**: Centralized package storage
- **Smart Caching**: Intelligent cache key strategies
- **Retention Policies**: Automated cleanup of old artifacts

### Package Signing
- **Supply Chain Security**: All packages are cryptographically signed
- **SBOM Generation**: Software Bill of Materials for transparency
- **Vulnerability Scanning**: Automated security scanning

### Build Metrics
- **Performance Tracking**: Build time and cache hit rate metrics
- **Quality Gates**: Automated quality validation
- **Compliance Reporting**: FIPS and security compliance reports

## Artifactory Setup

### Prerequisites

1. **Artifactory Access**: Contact the team for Artifactory credentials
2. **Conan Remote Configuration**: Set up Conan remote for Artifactory

### Configuration

```bash
# Add Artifactory remote
conan remote add artifactory https://your-artifactory.com/artifactory/api/conan/conan

# Configure authentication
conan user -p $ARTIFACTORY_PASSWORD -r artifactory $ARTIFACTORY_USERNAME

# Upload packages
conan upload "openssl/*" -r=artifactory --all --confirm
```

### Environment Variables

```bash
# Required for Artifactory integration
export ARTIFACTORY_URL="https://your-artifactory.com"
export ARTIFACTORY_USERNAME="your-username"
export ARTIFACTORY_PASSWORD="your-password"

# Optional: Package signing
export CONAN_SIGN_PACKAGES="true"
export COSIGN_PRIVATE_KEY="path/to/private.key"
```

## Local Development Workflow

### 1. Development Setup

```bash
# Clone repository
git clone https://github.com/sparesparrow/openssl.git
cd openssl

# Create development environment
conan install . --profile=linux-gcc-debug --build=missing

# Build locally
conan build .
```

### 2. Testing

```bash
# Run test package
conan create . --profile=linux-gcc-debug -o openssl:enable_unit_test=True

# Run specific tests
conan test test_package openssl/4.0.0@openssl/stable
```

### 3. Package Validation

```bash
# Validate package structure
conan create . --profile=linux-gcc-release
conan test test_package openssl/4.0.0@openssl/stable

# Check package info
conan info openssl/4.0.0@openssl/stable
```

### 4. Cross-Platform Testing

```bash
# Test on different platforms
conan create . --profile=linux-gcc-release
conan create . --profile=windows-msvc
conan create . --profile=macos-clang
```

## Advanced Configuration

### Custom Profiles

Create custom profiles for specific use cases:

```ini
# .conan/profiles/custom.profile
[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=12
build_type=Release

[options]
openssl:shared=True
openssl:fips=False
openssl:enable_quic=True
openssl:enable_zstd=True

[conf]
tools.build:skip_test=True
```

### Build Options

Key OpenSSL build options available:

| Option | Description | Default |
|--------|-------------|---------|
| `shared` | Build shared libraries | `True` |
| `fips` | Enable FIPS mode | `False` |
| `no_asm` | Disable assembly optimizations | `False` |
| `no_threads` | Disable threading support | `False` |
| `enable_quic` | Enable QUIC protocol support | `True` |
| `enable_demos` | Build demo applications | `False` |
| `enable_unit_test` | Build unit tests | `False` |
| `no_deprecated` | Disable deprecated APIs | `False` |

### Cache Management

```bash
# Clean cache
conan cache clean

# Clean specific package
conan cache clean openssl

# View cache info
conan cache info

# Remove old packages
conan cache clean --old
```

## Troubleshooting

### Common Issues

1. **Build Failures**:
   ```bash
   # Check build logs
   conan create . --profile=linux-gcc-debug -v
   
   # Clean and rebuild
   conan cache clean openssl
   conan create . --profile=linux-gcc-debug --build=missing
   ```

2. **FIPS Build Issues**:
   ```bash
   # Ensure FIPS profile is used
   conan create . --profile=linux-fips
   
   # Check FIPS configuration
   conan create . --profile=linux-fips -o openssl:enable_unit_test=True
   ```

3. **Cross-Platform Issues**:
   ```bash
   # Check platform-specific requirements
   conan install . --profile=windows-msvc --build=missing
   
   # Verify system requirements
   conan system_requirements
   ```

### Debug Information

```bash
# Verbose output
conan create . --profile=linux-gcc-debug -v

# Check package contents
conan package openssl/4.0.0@openssl/stable

# View package info
conan info openssl/4.0.0@openssl/stable --graph=graph.html
```

## CI/CD Integration

### GitHub Actions

The repository includes GitHub Actions workflows for:

- **Cross-repository CI**: Triggers builds in openssl-tools
- **Migration Controller**: Gradual migration with feature flags
- **Fast Lane CI**: Quick validation for small changes

### Feature Flags

Control CI behavior with PR labels:

- `conan-only`: Run only Conan CI
- `both-ci`: Run both legacy and Conan CI
- `legacy-only`: Run only legacy CI

### Matrix Builds

```yaml
# Example matrix configuration
strategy:
  matrix:
    include:
      - profile: linux-gcc-release
        platform: ubuntu-22.04
      - profile: linux-fips
        platform: ubuntu-22.04
      - profile: windows-msvc
        platform: windows-2022
      - profile: macos-clang
        platform: macos-12
```

## Security Features

### Supply Chain Security

- **Package Signing**: All packages are cryptographically signed
- **SBOM Generation**: Software Bill of Materials for transparency
- **Vulnerability Scanning**: Automated security scanning with Trivy/Snyk
- **License Compliance**: Dependency license validation

### FIPS Compliance

- **Separate Cache Keys**: Prevents FIPS/non-FIPS contamination
- **Compliance Validation**: Automated FIPS compliance checks
- **Audit Trails**: Complete build and deployment audit trails

## Performance Optimization

### Build Performance

- **Parallel Builds**: Multi-core compilation support
- **Intelligent Caching**: Smart cache key strategies
- **Incremental Builds**: Only rebuild changed components

### Cache Optimization

- **Multi-level Caching**: Local, shared, and remote caches
- **Cache Warming**: Pre-populate common configurations
- **Retention Policies**: Automated cleanup of old artifacts

## Support

### Documentation

- **Conan Documentation**: [docs.conan.io](https://docs.conan.io)
- **OpenSSL Documentation**: [openssl.org/docs](https://www.openssl.org/docs)
- **openssl-tools Repository**: [github.com/sparesparrow/openssl-tools](https://github.com/sparesparrow/openssl-tools)

### Getting Help

1. **Check logs**: Use `-v` flag for verbose output
2. **Clean cache**: Try `conan cache clean` for build issues
3. **Verify profiles**: Ensure correct profile is used
4. **Check dependencies**: Verify all dependencies are available

### Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test with multiple profiles**
5. **Submit a pull request**

## Migration from Legacy Builds

### Gradual Migration

The repository supports gradual migration from legacy builds:

1. **Phase 1**: Feature flags and parallel execution
2. **Phase 2**: Validation and comparison
3. **Phase 3**: Full migration to Conan CI

### Migration Controller

Use the migration controller to manage the transition:

```bash
# Test with Conan CI only
# Add label: conan-only

# Compare both systems
# Add label: both-ci

# Use legacy CI only
# Add label: legacy-only
```

This ensures a smooth transition with minimal risk and maximum validation.