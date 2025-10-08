# OpenSSL Conan Build Matrix Configuration Guide

## Overview
This configuration translates OpenSSL's complex ./config build system into
Conan-compatible profiles and options, enabling cross-platform reproducible builds.

## Profile Structure

Profiles are located in `conan-dev/profiles/` and define:
- Operating System (Linux, macOS, FreeBSD)
- Architecture (x86_64, armv8)
- Compiler (gcc, clang, apple-clang) and version
- Build environment variables

## Available Profiles

1. **linux-gcc11** - Linux with GCC 11 (default)
2. **linux-clang15** - Linux with Clang 15
3. **linux-arm64-gcc** - Linux ARM64 with GCC
4. **macos-x86_64** - macOS Intel with Apple Clang
5. **macos-arm64** - macOS Apple Silicon with Apple Clang
6. **freebsd-x86_64** - FreeBSD with GCC
7. **linux-gcc11-debug** - Linux GCC Debug build
8. **linux-clang15-debug** - Linux Clang Debug build

## Build Options

### Core Options
- `shared=[True|False]` - Build shared/static libraries
- `fPIC=[True|False]` - Position Independent Code
- `fips=[True|False]` - FIPS 140-2/3 compliance mode

### Feature Options
- `enable_demos` - Build demo applications
- `enable_h3demo` - Build HTTP/3 demos
- `enable_quic` - QUIC protocol support
- `enable_sslkeylog` - SSL keylog for debugging

### Security Options
- `no_deprecated` - Disable deprecated APIs
- `enable_weak_ssl_ciphers` - Enable weak ciphers (testing only)
- `enable_ssl3` - Enable SSL 3.0 (insecure)

### Debug & Sanitizer Options
- `enable_asan` - Address Sanitizer
- `enable_ubsan` - Undefined Behavior Sanitizer
- `enable_msan` - Memory Sanitizer
- `enable_tsan` - Thread Sanitizer
- `enable_crypto_mdebug` - Crypto memory debugging

### Performance Options
- `no_asm` - Disable assembly optimizations
- `no_threads` - Disable threading support
- `no_bulk` - Disable bulk encryption

### System Integration
- `enable_ktls` - Kernel TLS support
- `enable_sctp` - SCTP protocol support
- `enable_zlib` - zlib compression
- `enable_zstd` - zstd compression

## Example Configurations

### Basic FIPS Build
```bash
conan create . --profile=conan-dev/profiles/linux-gcc11 \
  -o fips=True \
  -o shared=True
```

### Debug Build with Sanitizers
```bash
conan create . --profile=conan-dev/profiles/linux-clang15-debug \
  -s build_type=Debug \
  -o enable_asan=True \
  -o enable_ubsan=True \
  -o fips=True
```

### Minimal Static Build
```bash
conan create . --profile=conan-dev/profiles/linux-gcc11 \
  -o shared=False \
  -o no_bulk=True \
  -o no_asm=True \
  -o fips=False
```

### Full-Featured Build
```bash
conan create . --profile=conan-dev/profiles/linux-gcc11 \
  -o fips=True \
  -o enable_ktls=True \
  -o enable_zlib=True \
  -o enable_zstd=True \
  -o enable_sctp=True
```

## CI/CD Integration

The provided GitHub Actions workflow automatically tests:
- All platform combinations
- Key configuration variants
- Sanitizer builds
- Static and shared builds

To customize CI builds, modify the matrix in `.github/workflows/conan-ci.yml`

## Mapping from OpenSSL ./config

| OpenSSL ./config flag | Conan option |
|-----------------------|--------------|
| `--debug` | `-s build_type=Debug` |
| `enable-fips` | `-o fips=True` |
| `no-shared` | `-o shared=False` |
| `enable-asan` | `-o enable_asan=True` |
| `enable-ktls` | `-o enable_ktls=True` |
| `no-deprecated` | `-o no_deprecated=True` |
| `no-asm` | `-o no_asm=True` |

## Build Type Matrix

| Build Type | Typical Options | Use Case |
|------------|----------------|----------|
| Production | `fips=True, shared=True` | Production deployments |
| Development | `build_type=Debug, enable_crypto_mdebug=True` | Local development |
| Testing | `enable_asan=True, enable_ubsan=True` | CI/CD testing |
| Minimal | `shared=False, no_bulk=True, no_asm=True` | Embedded systems |
| Full | `fips=True, enable_ktls=True, enable_zlib=True` | Full feature set |

## Platform-Specific Notes

### Linux
- Supports all options
- Recommended for FIPS validation
- Best sanitizer support

### macOS
- Limited FIPS support
- Apple Clang compiler required
- ARM64 (M1/M2/M3) fully supported

### FreeBSD
- Basic support
- No FIPS validation
- Limited sanitizer support

## Troubleshooting

### Missing dependencies
```bash
# Install system dependencies first
sudo apt-get install build-essential perl

# Then install with Conan
conan install . --build=missing
```

### Profile detection fails
```bash
# Manually create profile
conan profile detect --force

# Or use specific profile
conan install . --profile=conan-dev/profiles/linux-gcc11
```

### Build fails with sanitizers
- Ensure `build_type=Debug`
- Some sanitizers (msan, tsan) require `shared=False`
- Not all options are compatible with all sanitizers

## Support Matrix

| Platform | FIPS | Sanitizers | Threading | KTLS |
|----------|------|------------|-----------|------|
| Linux x86_64 | ✅ | ✅ | ✅ | ✅ |
| Linux ARM64 | ✅ | ✅ | ✅ | ✅ |
| macOS x86_64 | ⚠️ | ⚠️ | ✅ | ❌ |
| macOS ARM64 | ⚠️ | ⚠️ | ✅ | ❌ |
| FreeBSD | ❌ | ❌ | ✅ | ❌ |

Legend:
- ✅ Full support
- ⚠️ Partial support
- ❌ Not supported