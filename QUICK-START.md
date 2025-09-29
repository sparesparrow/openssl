# Quick Start Guide: Modern OpenSSL CI/CD with Conan

This guide helps you quickly get started with the modernized OpenSSL CI/CD system using Conan dependency management.

## Prerequisites

- Python 3.8+ with pip
- Docker (optional, for containerized development)
- Git
- Basic familiarity with CI/CD concepts

## 1. Local Development Setup

### Install Conan
```bash
# Install Conan package manager
pip install conan==2.0.17

# Verify installation
conan --version
```

### Configure Conan
```bash
# Detect and create default profile
conan profile detect --force

# Add Conan Center repository
conan remote add conancenter https://center.conan.io

# (Optional) Add your organization's Conan repository
conan remote add openssl-artifacts https://artifacts.yourorg.com/conan
```

### Clone and Build OpenSSL
```bash
# Clone the repository
git clone https://github.com/openssl/openssl.git
cd openssl

# Build with default configuration
conan create . --profile=conan-profiles/ci-linux-gcc.profile --build=missing

# Or install dependencies and build manually
conan install . --profile=conan-profiles/ci-linux-gcc.profile --build=missing
./config --strict-warnings enable-fips
make -j$(nproc)
make test
```

## 2. Using Docker Development Environment

### Start Development Environment
```bash
# Start the complete development environment
docker-compose -f docker-compose.dev.yml up -d openssl-dev

# Enter the development container
docker exec -it openssl-dev bash

# Inside the container, build OpenSSL
conan create . --profile=conan-profiles/ci-linux-gcc.profile --build=missing
```

### Run Specific Test Environments
```bash
# Run sanitizer tests
docker-compose -f docker-compose.dev.yml up openssl-sanitizers

# Run performance tests
docker-compose -f docker-compose.dev.yml up openssl-perf

# Generate documentation
docker-compose -f docker-compose.dev.yml up openssl-docs
```

## 3. Available Conan Profiles

### Standard Profiles
- `ci-linux-gcc.profile` - Standard Linux GCC build
- `ci-linux-clang.profile` - Linux Clang build
- `ci-sanitizers.profile` - Build with sanitizers enabled
- `ci-macos-x64.profile` - macOS Intel build
- `ci-macos-arm64.profile` - macOS Apple Silicon build

### Profile Usage Examples
```bash
# GCC build with FIPS
conan create . --profile=conan-profiles/ci-linux-gcc.profile

# Clang build without FIPS
conan create . --profile=conan-profiles/ci-linux-clang.profile

# Debug build with sanitizers
conan create . --profile=conan-profiles/ci-sanitizers.profile

# Custom profile modifications
cp conan-profiles/ci-linux-gcc.profile my-custom.profile
# Edit my-custom.profile as needed
conan create . --profile=my-custom.profile
```

## 4. Common Build Configurations

### Development Build (Debug + Tests)
```bash
conan create . \
  --profile=conan-profiles/ci-linux-gcc.profile \
  -o openssl/*:enable_unit_test=True \
  -o openssl/*:enable_crypto_mdebug=True \
  -s build_type=Debug
```

### Production Build (Optimized)
```bash
conan create . \
  --profile=conan-profiles/ci-linux-gcc.profile \
  -o openssl/*:shared=True \
  -o openssl/*:fips=True \
  -s build_type=Release
```

### Security Testing Build
```bash
conan create . \
  --profile=conan-profiles/ci-sanitizers.profile \
  -o openssl/*:enable_asan=True \
  -o openssl/*:enable_ubsan=True
```

## 5. CI/CD Integration

### GitHub Actions
The modern CI workflow is defined in `.github/workflows/modern-ci.yml`. It automatically:
- Detects changes and runs appropriate tests
- Uses Conan for dependency management
- Implements security scanning
- Generates build artifacts and reports

### Key Features
- **Intelligent caching**: Reuses build artifacts across jobs
- **Security scanning**: Automated vulnerability detection
- **SBOM generation**: Software Bill of Materials for compliance
- **Multi-platform**: Supports Linux, macOS, Windows
- **Sanitizer testing**: Memory safety validation

## 6. Customization

### Adding New Build Options
Edit `conanfile.py` to add new options:
```python
options = {
    # ... existing options ...
    "my_new_option": [True, False],
}

default_options = {
    # ... existing defaults ...
    "my_new_option": False,
}
```

### Creating Custom Profiles
```bash
# Copy existing profile
cp conan-profiles/ci-linux-gcc.profile conan-profiles/my-profile.profile

# Edit the profile
vim conan-profiles/my-profile.profile

# Use the custom profile
conan create . --profile=conan-profiles/my-profile.profile
```

### Modifying CI Workflow
Edit `.github/workflows/modern-ci.yml` to:
- Add new build matrices
- Modify test configurations
- Add custom validation steps
- Integrate with additional tools

## 7. Troubleshooting

### Common Issues

#### Conan Profile Not Found
```bash
# Error: Profile not found
# Solution: Ensure profile exists and path is correct
ls conan-profiles/
conan profile show conan-profiles/ci-linux-gcc.profile
```

#### Build Dependencies Missing
```bash
# Error: Missing dependencies
# Solution: Install system dependencies
sudo apt-get update
sudo apt-get install build-essential perl

# Or use Docker environment
docker-compose -f docker-compose.dev.yml up -d openssl-dev
```

#### Cache Issues
```bash
# Clear Conan cache
conan cache path  # Show cache location
conan remove "*" --confirm  # Clear all packages

# Or remove specific packages
conan remove "openssl/*" --confirm
```

### Getting Help
1. Check the [Migration Guide](MIGRATION-GUIDE.md) for detailed information
2. Review the [CI/CD Analysis](CICD-ANALYSIS-AND-MODERNIZATION.md) for background
3. Examine existing profiles in `conan-profiles/` directory
4. Look at the Docker setup in `docker-compose.dev.yml`
5. Check CI workflow examples in `.github/workflows/modern-ci.yml`

## 8. Next Steps

1. **Familiarize yourself** with Conan concepts and commands
2. **Experiment** with different build configurations
3. **Integrate** with your development workflow
4. **Customize** profiles and options for your needs
5. **Contribute** improvements back to the project

## 9. Performance Tips

### Faster Builds
- Use `--build=missing` to avoid rebuilding existing packages
- Enable parallel builds with `-c tools.build:jobs=$(nproc)`
- Use Docker for consistent environments
- Leverage Conan's binary caching

### Development Workflow
- Use development containers for consistency
- Create custom profiles for common configurations
- Use incremental builds during development
- Run tests selectively during development

### CI Optimization
- Use GitHub Actions cache for Conan packages
- Implement smart job scheduling based on changes
- Use matrix builds efficiently
- Monitor and optimize resource usage

This quick start guide should get you up and running with the modern OpenSSL CI/CD system. For more detailed information, refer to the comprehensive documentation files included in this modernization package.