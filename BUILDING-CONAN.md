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
conan user -p $ARTIFACTORY_URL -r artifactory $ARTIFACTORY_USERNAME

# Upload packages
conan upload "openssl/*" -r=artifactory --confirm
```

### Environment Variables

```bash
# Required for Artifactory integration
export ARTIFACTORY_URL="https://your-artifactory.com"
export ARTIFACTORY_USERNAME="your-username"
export ARTIFACTORY_URL="your-password"

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

## Troubleshooting

### Common Issues and Solutions

#### Build Failures

**Error: "Missing system dependencies"**
```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential cmake git perl libperl-dev

# On CentOS/RHEL
sudo yum install gcc gcc-c++ make cmake git perl perl-devel

# On macOS
xcode-select --install
brew install cmake perl

# On Windows
# Install Visual Studio 2022 or Visual Studio Build Tools
# Install CMake and Perl (Strawberry Perl recommended)
```

**Error: "CMake configuration failed"**
```bash
# Clean build directory
rm -rf build/

# Regenerate CMake cache
conan install . --build missing

# Check CMake version (requires 3.15+)
cmake --version
```

**Error: "FIPS module validation failed"**
```bash
# Ensure FIPS profile is used
conan create . --profile=linux-fips

# Check FIPS-specific requirements
conan create . --profile=linux-fips -o openssl:enable_tests=True
```

#### Dependency Issues

**Error: "Package not found in remotes"**
```bash
# Add required remotes
conan remote add conancenter https://center.conan.io
conan remote add cloudsmith https://cloudsmith.io/sparesparrow/openssl/

# Update remote information
conan remote update conancenter
```

**Error: "Incompatible compiler version"**
```bash
# Check compiler requirements
conan profile show

# Update compiler if needed
# GCC 7+ required for FIPS mode
# Visual Studio 2019+ recommended
```

#### Performance Issues

**Error: "Build takes too long"**
```bash
# Use optimized profile
conan create . --profile=linux-gcc-release

# Enable parallel builds
conan create . --profile=linux-gcc-release -j$(nproc)

# Clean cache for fresh start
conan cache clean --source --build --download
```

### Platform-Specific Issues

#### Linux

**Error: "libperl.so not found"**
```bash
# Install libperl-dev
sudo apt-get install libperl-dev

# Check Perl installation
perl -v
```

**Error: "CMake cannot find OpenSSL"**
```bash
# Avoid system OpenSSL conflicts
export OPENSSL_ROOT_DIR=/usr/local
# Or use containerized builds
```

#### Windows

**Error: "MSVC compiler not found"**
```bash
# Install Visual Studio Build Tools
# Ensure MSVC 2019+ is in PATH
# Check with: cl
```

**Error: "Perl not found"**
```bash
# Install Strawberry Perl
# Add to PATH: C:\Strawberry\perl\bin
```

#### macOS

**Error: "Command Line Tools not installed"**
```bash
xcode-select --install
```

**Error: "Architecture mismatch"**
```bash
# Check target architecture
conan profile show

# Use correct profile for ARM64
conan create . --profile=macos-clang
```

### Debug and Diagnostics

#### Verbose Output
```bash
# Enable verbose Conan output
conan create . --profile=linux-gcc-release -v

# Debug CMake configuration
conan install . --build missing -if build -v
cd build && cmake .. -DCMAKE_BUILD_TYPE=Debug
```

#### Log Analysis
```bash
# Check Conan logs
conan cache logs openssl/4.0.0-dev@user/stable

# Check build logs in CI
# Navigate to Actions tab in GitHub
```

#### Cache Issues
```bash
# Clean all caches
conan cache clean --all

# Clean specific package
conan cache clean openssl/4.0.0-dev@user/stable

# Reset profile cache
conan profile detect --force
```

## Migration from Legacy Builds

### Migration Guide

This section provides a comprehensive guide for migrating from traditional OpenSSL builds to Conan-based builds.

#### Assessment Phase

1. **Identify Current Build Process**
   ```bash
   # Document current build commands
   ./Configure --prefix=/usr/local --openssldir=/etc/ssl
   make
   make install

   # Or traditional CMake
   mkdir build && cd build
   cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
   make install
   ```

2. **Inventory Dependencies**
   ```bash
   # List system dependencies
   ldd /usr/local/lib/libssl.so
   ldd /usr/local/lib/libcrypto.so
   ```

3. **Document Configuration**
   - Compiler versions and flags
   - Installation paths
   - Environment variables
   - Platform-specific settings

#### Planning Phase

1. **Choose Migration Strategy**
   - **Parallel**: Run both systems simultaneously
   - **Gradual**: Phase out legacy builds incrementally
   - **Big Bang**: Complete switch to Conan

2. **Identify Conan Profiles**
   ```bash
   # Map legacy configurations to Conan profiles
   # GCC release -> linux-gcc-release
   # MSVC debug -> windows-msvc-debug
   # FIPS builds -> linux-fips
   ```

3. **Plan Testing Strategy**
   - Unit tests for functionality
   - Integration tests for compatibility
   - Performance benchmarks
   - Security validation

#### Implementation Phase

1. **Install Conan**
   ```bash
   pip install conan
   conan profile detect --force
   ```

2. **Create Test Package**
   ```bash
   # Test basic functionality
   conan create . --profile=linux-gcc-release

   # Verify installation
   conan test test_package
   ```

3. **Compare Outputs**
   ```bash
   # Traditional build
   ./Configure --prefix=/tmp/openssl-traditional
   make && make install

   # Conan build
   conan create . --profile=linux-gcc-release \
     --output-folder=/tmp/openssl-conan

   # Compare
   diff -r /tmp/openssl-traditional /tmp/openssl-conan
   ```

4. **Update Build Scripts**
   ```bash
   # Replace traditional commands with Conan
   # Old:
   # ./Configure && make && make install

   # New:
   conan create . --profile=production
   ```

#### Validation Phase

1. **Functional Testing**
   ```bash
   # Test cryptographic operations
   openssl speed aes-256-cbc

   # Test SSL/TLS
   openssl s_client -connect google.com:443

   # Test FIPS mode (if applicable)
   openssl md5 /dev/null  # Should fail in FIPS mode
   ```

2. **Compatibility Testing**
   ```bash
   # Test with existing applications
   # Compile and run consumer projects
   conan test consumer_test/
   ```

3. **Performance Validation**
   ```bash
   # Benchmark comparison
   openssl speed -elapsed aes-256-cbc
   openssl speed -elapsed sha256
   ```

#### Rollback Strategy

1. **Maintain Legacy Builds**
   - Keep traditional build scripts
   - Preserve existing installations
   - Plan rollback procedures

2. **Gradual Migration Controller**
   ```bash
   # Use migration labels in CI
   # conan-only: Test Conan builds only
   # both-ci: Run both traditional and Conan
   # legacy-only: Traditional builds only
   ```

3. **Rollback Commands**
   ```bash
   # Quick rollback to legacy
   ./Configure --prefix=/usr/local
   make clean
   make && make install

   # Restore from backup
   cp -r /backup/openssl-backup/* /usr/local/
   ```

#### Post-Migration

1. **Update Documentation**
   - Update build instructions
   - Document new procedures
   - Update team training

2. **Monitor Performance**
   - Track build times
   - Monitor cache hit rates
   - Watch for regressions

3. **Gather Feedback**
   - Collect team experiences
   - Document lessons learned
   - Plan improvements

### Migration Checklist

- [ ] Document current build process
- [ ] Install Conan and verify setup
- [ ] Create equivalent Conan profiles
- [ ] Test package creation
- [ ] Compare build outputs
- [ ] Validate functionality
- [ ] Test consumer applications
- [ ] Update build scripts
- [ ] Plan rollback strategy
- [ ] Train team members
- [ ] Monitor and optimize

This ensures a smooth transition with minimal risk and maximum validation.