# OpenSSL Build Matrix - Complete Conan Translation

## Summary Statistics

- **Total CI Jobs in OpenSSL**: 25+ configurations
- **Platforms**: 5 (Linux x86_64, Linux ARM64, macOS x86_64, macOS ARM64, FreeBSD)
- **Compilers**: 2 primary (GCC, Clang/Apple Clang)
- **Build Types**: 2 (Release, Debug)
- **Conan Options**: 35+ configurable options
- **Conan Profiles**: 8 pre-configured profiles

## Key Insights

### 1. Build Complexity
OpenSSL uses a sophisticated ./config script with 100+ command-line options.
This Conan translation maps the most important ~35 options while maintaining
compatibility with the existing build system.

### 2. Platform Coverage
```
┌─────────────┬──────────┬─────────┬──────────┬────────────┐
│ Platform    │ Compiler │ FIPS    │ Testing  │ Priority   │
├─────────────┼──────────┼─────────┼──────────┼────────────┤
│ Linux x86   │ GCC      │ Full    │ Complete │ Primary    │
│ Linux x86   │ Clang    │ Full    │ Complete │ Primary    │
│ Linux ARM64 │ GCC      │ Full    │ Complete │ Primary    │
│ macOS x86   │ Clang    │ Partial │ Complete │ Secondary  │
│ macOS ARM64 │ Clang    │ Partial │ Complete │ Secondary  │
│ FreeBSD     │ GCC      │ None    │ Basic    │ Community  │
└─────────────┴──────────┴─────────┴──────────┴────────────┘
```

### 3. Most Common Configurations

From analysis of OpenSSL CI, these are the most tested configurations:

**Production-Ready:**
1. Linux x86_64 GCC + FIPS + shared
2. Linux ARM64 GCC + FIPS + shared
3. macOS ARM64 Clang + FIPS + shared

**Development:**
1. Linux x86_64 Clang + Debug + ASAN/UBSAN
2. Linux x86_64 GCC + Debug + crypto_mdebug

**Special Purpose:**
1. Minimal build (no-asm, no-bulk, static)
2. No-deprecated (API compatibility testing)
3. Full-featured (all protocols, all algorithms)

## Conan Command Reference

### Quick Start (Most Common)

```bash
# Production FIPS build
conan create . --profile=conan-dev/profiles/linux-gcc11 \
  -o fips=True

# Development build with debugging
conan create . --profile=conan-dev/profiles/linux-gcc11 \
  -s build_type=Debug \
  -o enable_crypto_mdebug=True

# CI testing with sanitizers
conan create . --profile=conan-dev/profiles/linux-clang15-debug \
  -s build_type=Debug \
  -o enable_asan=True \
  -o enable_ubsan=True
```

### All Configurations from OpenSSL CI

| Job Name | Platform | Compiler | Build Type | Key Options | Conan Command |
|----------|----------|----------|------------|-------------|---------------|
| basic_gcc | linux-x86_64 | gcc | Release | fips=True | `conan create . --profile=linux-gcc11 \\
  -o fips=True` |
| basic_clang | linux-x86_64 | clang | Release | defaults | `conan create . --profile=linux-clang15` |
| linux-arm64 | linux-arm64 | gcc | Release | fips=True | `conan create . --profile=linux-arm64-gcc \\
  -o fips=True` |
| minimal | linux-x86_64 | gcc | Release | defaults | `conan create . --profile=linux-gcc11` |
| no-deprecated | linux-x86_64 | gcc | Release | fips=True | `conan create . --profile=linux-gcc11 \\
  -o fips=True` |
| no-shared-ubuntu | linux-x86_64 | gcc | Release | shared=False | `conan create . --profile=linux-gcc11 \\
  -o shared=False` |
| address_ub_sanitizer | linux-x86_64 | gcc | Debug | fips=True, enable_asan=True, enable_ubsan=True | `conan create . --profile=linux-gcc11-debug \\
  -o fips=True \\
  -o enable_asan=True \\
  -o enable_ubsan=True` |
| memory_sanitizer | linux-x86_64 | clang | Debug | fips=True, shared=False | `conan create . --profile=linux-clang15-debug \\
  -o fips=True \\
  -o shared=False` |

## Option Groups

### Security & Compliance
- `fips` - FIPS 140-2/3 validated cryptography
- `no_deprecated` - Remove deprecated APIs
- `enable_weak_ssl_ciphers` - Include weak ciphers (testing only)

### Protocol Support  
- `enable_quic` - QUIC protocol
- `enable_ssl3` - SSL 3.0 (insecure, deprecated)
- `no_dtls` - Disable DTLS
- `no_tls1`, `no_tls1_1` - Disable older TLS versions

### Performance
- `no_asm` - Disable assembly optimizations
- `no_threads` - Single-threaded mode
- `no_bulk` - Disable bulk encryption
- `enable_ktls` - Kernel TLS offload

### Debugging
- `enable_crypto_mdebug` - Memory debugging
- `enable_trace` - Protocol tracing
- `enable_asan` - Address Sanitizer
- `enable_ubsan` - Undefined Behavior Sanitizer
- `enable_msan` - Memory Sanitizer
- `enable_tsan` - Thread Sanitizer

### Algorithms
- `enable_md2`, `enable_md4` - Weak hashes (legacy)
- `enable_rc5` - RC5 encryption
- `enable_ec_nistp_64_gcc_128` - Optimized EC

### System Integration
- `enable_zlib` - zlib compression
- `enable_zstd` - zstd compression
- `enable_sctp` - SCTP protocol
- `enable_ktls` - Kernel TLS

## File Structure

```
conan-dev/
├── profiles/
│   ├── linux-gcc11           # Linux GCC profile
│   ├── linux-clang15         # Linux Clang profile
│   ├── linux-arm64-gcc       # Linux ARM64 profile
│   ├── macos-x86_64          # macOS Intel profile
│   ├── macos-arm64           # macOS ARM profile
│   ├── freebsd-x86_64        # FreeBSD profile
│   ├── linux-gcc11-debug     # Linux GCC Debug profile
│   └── linux-clang15-debug   # Linux Clang Debug profile
├── conanfile.py              # Main Conan recipe
├── openssl_build_matrix.json # Build matrix configuration
└── conandata.yml             # Version data

.github/
└── workflows/
    └── conan-ci.yml          # CI/CD automation

docs/
├── CONAN_BUILD_MATRIX_GUIDE.md  # This guide
└── OPENSSL_CONAN_COMPLETE_REFERENCE.md  # Complete reference
```

## Migration Path from Bash Scripts

For developers currently using bash scripts:

**Old approach:**
```bash
./config --strict-warnings enable-fips enable-demos
make -j$(nproc)
make test
make install DESTDIR=/path/to/install
```

**New Conan approach:**
```bash
# One-time setup
python scripts/conan/conan_cli.py setup

# Build and test
conan create . --profile=linux-gcc11 -o fips=True -o enable_demos=True

# Install to specific location
conan install . --install-folder=/path/to/install
```

## Benefits Over Traditional Build

1. **Reproducibility**: Lockfiles ensure exact same dependencies
2. **Cross-platform**: Same commands work on Linux, macOS, Windows
3. **Dependency Management**: Automatic handling of build tools (Perl, etc.)
4. **CI/CD Integration**: Native GitHub Actions support
5. **Package Distribution**: Easy sharing of built artifacts
6. **Configuration Management**: Profiles handle platform differences

## Limitations & Considerations

### What Conan Doesn't Replace
- OpenSSL's actual build system (./config, make)
- Platform-specific build logic
- Custom Perl scripts for code generation

### What Conan Adds
- Unified interface across platforms
- Dependency management
- Package distribution
- CI/CD automation
- Configuration management

## Testing Strategy

Recommended testing matrix for pull requests:

**Minimum (Fast Feedback):**
- Linux x86_64 GCC Release + FIPS
- Linux x86_64 Clang Debug + ASAN/UBSAN

**Standard (Comprehensive):**
- All platforms (Linux x86/ARM, macOS x86/ARM)
- Both GCC and Clang
- FIPS and non-FIPS builds
- Static and shared builds

**Extended (Pre-Release):**
- All standard tests
- All sanitizer combinations
- Special configurations (minimal, full-featured)
- External integration tests

## Support & Resources

- OpenSSL CI reference: `.github/workflows/conan-ci.yml`
- Conan documentation: https://docs.conan.io/2/
- Profile templates: `conan-dev/profiles/`
- Build matrix: `conan-dev/openssl_build_matrix.json`

---

Generated from OpenSSL CI configuration analysis
Date: October 2025
Compatible with: OpenSSL 3.x, Conan 2.x