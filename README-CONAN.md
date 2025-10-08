# OpenSSL Conan Development Environment

Cross-platform Python-based Conan development environment for OpenSSL with advanced CI/CD patterns.

## 🚀 Quick Start

### Setup Environment
```bash
# Cross-platform setup
python scripts/setup-conan-python-env.py

# Or use the orchestrator directly
python scripts/conan/conan_cli.py setup
```

### Developer Commands
```bash
# Using Python CLI (cross-platform)
python scripts/conan/conan_cli.py install
python scripts/conan/conan_cli.py build
python scripts/conan/conan_cli.py test

# Using platform-specific launchers
# Windows: conan-install.bat, conan-build.bat
# Unix/Linux/macOS: ./conan-install, ./conan-build
```

## 🖥️ Platform Support

- **Windows**: MSVC 2022, Debug/Release profiles
- **macOS**: Clang 14, Universal and ARM64 support
- **Linux**: GCC 11, Clang 15, multiple architectures

## 🔧 Key Features

### Cross-Platform Orchestration
- Unified Python CLI across all platforms
- Automatic platform detection and profile selection
- Virtual environment management
- Comprehensive error handling

### Advanced CI/CD Patterns
- **Dependency Management**: Automated updates with vulnerability scanning
- **Code Quality**: Static analysis, coverage metrics, quality gates
- **Database Validation**: Schema comparison and integrity checks
- **Log Management**: Deterministic CI logs with pattern filtering
- **Security**: SBOM generation, license compliance, vulnerability scanning
- **Performance**: Benchmarking with baseline comparison

### Enterprise-Grade Quality
- Hermetic build environments with pinned toolchains
- Multi-level caching strategies for optimal performance
- Comprehensive testing with quality gates
- Security-first approach with compliance validation
- Performance monitoring with regression detection

## 📁 Directory Structure

```
scripts/conan/
├── conan_orchestrator.py      # Core orchestrator
├── conan_cli.py              # Unified CLI
├── dependency_manager.py     # Automated dependency management
├── code_quality_manager.py   # Code quality and static analysis
├── database_schema_validator.py # Database validation
├── log_whitelist_manager.py  # Log filtering and management
├── performance_benchmark.py  # Performance testing
├── test_harness.py          # Advanced test framework
└── [platform launchers]     # .bat files (Windows) and scripts (Unix)
```

## 🎯 Usage Examples

### Basic Usage
```bash
# Setup (one time)
python scripts/conan/conan_cli.py setup

# Install dependencies
python scripts/conan/conan_cli.py install

# Build package
python scripts/conan/conan_cli.py build

# Build and test
python scripts/conan/conan_cli.py build --test
```

### Advanced Features
```bash
# Check for dependency updates
python scripts/conan/dependency_manager.py --action check-updates

# Run code quality analysis
python scripts/conan/code_quality_manager.py --action full-report

# Validate database schemas
python scripts/conan/database_schema_validator.py --action validate

# Run performance benchmarks
python scripts/conan/performance_benchmark.py --action benchmark
```

## 🔄 CI/CD Integration

The CI/CD workflows provide:
- Multi-platform build matrix (Linux, Windows, macOS)
- Comprehensive testing and validation
- Performance benchmarking with baseline comparison
- Security scanning and compliance checking
- Automated package upload and release management

## 🛠️ Configuration

### Environment Variables
```bash
# Conan configuration
CONAN_CPU_COUNT=4
CONAN_VERSION=2.0

# Security scanning
SONAR_TOKEN=your_sonar_token
ARTIFACTORY_URL=your_artifactory_url

# Schema validation
SCHEMA_MISMATCH_RAISE_ERROR=1  # Set to 0 to allow mismatches

# Log filtering
LOG_FILTERS=conan-dev/log-whitelist.yml
```

### Configuration Files
- `conan-dev/dependency-config.yml`: Dependency management
- `conan-dev/quality-config.yml`: Code quality settings
- `conan-dev/schema-config.yml`: Database validation
- `conan-dev/log-whitelist.yml`: Log filtering patterns

## 📚 Documentation

- [**CONAN-PYTHON-ENVIRONMENT.md**](CONAN-PYTHON-ENVIRONMENT.md): Detailed environment setup
- [**ADVANCED-CICD-PATTERNS.md**](ADVANCED-CICD-PATTERNS.md): Enterprise CI/CD patterns
- [**IMPLEMENTATION-SUMMARY.md**](IMPLEMENTATION-SUMMARY.md): Complete implementation overview

## 🤝 Contributing

1. Fork the repository
2. Make changes to Python scripts
3. Test on multiple platforms
4. Submit a pull request

The Python orchestrator makes it easy to add new features and platforms.

## 📈 Benefits

### Cross-Platform
- Works on Windows, macOS, and Linux
- Platform-specific optimizations
- Unified command interface

### Python-Based
- Better error handling
- Rich logging and output
- Extensible and maintainable

### Developer-Friendly
- Simple commands
- Helpful error messages
- Comprehensive documentation

### Enterprise-Ready
- Security-first approach
- Comprehensive testing
- Performance monitoring
- Compliance validation
