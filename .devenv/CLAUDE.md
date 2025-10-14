# OpenSSL Fork - AI Context

**Role**: Domain layer providing OpenSSL cryptographic library

**Architecture**: 5-phase build process
1. Source preparation + integrity validation
2. Configure script execution  
3. Build execution (make/nmake)
4. Self-test validation
5. FIPS module validation (conditional)

**Deployment Targets**:
- general: Standard applications
- fips-government: FIPS 140-3 Certificate #4985
- embedded: Optimized static builds

**Key Features**:
- Multi-phase build with validation at each step
- SBOM generation with compliance metadata
- Platform-specific configuration (Linux/Windows/macOS)
- Comprehensive test coverage
