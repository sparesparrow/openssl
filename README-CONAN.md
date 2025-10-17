# OpenSSL + Conan Integration

This **minimal** `conanfile.py` is provided for **development and testing only**.

## Production Usage

For production use, refer to:
- **[sparesparrow/openssl-tools](https://github.com/sparesparrow/openssl-tools)** - Python_requires with full build orchestration
- **[sparesparrow/openssl-conan-base](https://github.com/sparesparrow/openssl-conan-base)** - Production recipes and profiles
- **[Cloudsmith Repository](https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/)** - Pre-built artifacts and packages

## Architecture Overview

```
OpenSSL Ecosystem (sparesparrow)
├── openssl/                    # Upstream fork (minimal conanfile.py)
├── openssl-tools/             # Python_requires + extensions
├── openssl-conan-base/        # Profiles + CI/CD
└── openssl-fips-policy/       # FIPS certificates
```

## Local Testing

```bash
# Basic build (requires openssl-tools python_requires)
conan create . --build=missing --profile=default
```

## Development Workflow

### 1. Export openssl-tools python_requires
```bash
cd openssl-tools
conan export . --name=openssl-tools --version=1.2.0
```

### 2. Use custom build command
```bash
# Simplified build with FIPS
conan openssl:build --fips --profile=linux-gcc11-fips

# Analyze dependencies
conan openssl:graph --json
```

### 3. Advanced deployment
```bash
# Build with enhanced deployer (includes SBOM)
conan install . \
  --requires="openssl/[>=3.0 <4.0]" \
  --deployer=full_deploy_enhanced \
  --deployer-folder=./artifacts
```

## Files Generated

- `sbom.json` - CycloneDX Software Bill of Materials
- `fips/` - FIPS-specific artifacts (when FIPS enabled)
- `full_deploy/` - Complete deployment bundle

## Troubleshooting

### Missing Extensions
```bash
# Install extensions
conan config install https://github.com/sparesparrow/openssl-tools.git
```

### Build Failures
```bash
# Check available profiles
conan profile list

# Use specific profile
conan create . --profile=linux-gcc11-fips --build=missing
```

### Dependency Issues
```bash
# Clean cache
conan cache clean

# Update remotes
conan remote update sparesparrow-conan
```

## Security & Compliance

- **SBOM Generation**: Automatic CycloneDX format SBOMs
- **FIPS Support**: Certificate #4985 integration
- **Vulnerability Scanning**: Integrated with security tools
- **Supply Chain**: Signed releases and reproducible builds

## Contributing

See [sparesparrow/openssl-tools](https://github.com/sparesparrow/openssl-tools) for advanced workflows and contribution guidelines.
