# OpenSSL FIPS DDD Workspace

This workspace provides a comprehensive development environment for OpenSSL FIPS development using Domain-Driven Design (DDD) layered architecture principles.

## 🏗️ Workspace Structure

### Repository Organization

```
openssl-ddd-workspace/
├── 🏠 Core Development: OpenSSL (main repository)
│   ├── 🔬 Domain: Crypto Core (crypto/)
│   ├── 🛡️ Application: SSL/TLS Protocols (ssl/)
│   ├── 🔧 Infrastructure: Providers & FIPS (providers/)
│   ├── 📱 Presentation: CLI & APIs (apps/)
│   ├── 🧪 Testing: FIPS Validation (test/)
│   └── 📚 Documentation: OpenSSL Docs (doc/)
├── 🏗️ Foundation: OpenSSL Conan Base (../openssl-conan-base/)
│   ├── Python virtual environment setup
│   ├── Conan package definitions
│   └── Base dependencies
├── 🛠️ Tooling: OpenSSL Tools (../openssl-tools/)
│   ├── Workflow orchestration scripts
│   ├── Testing utilities
│   ├── Monitoring dashboard
│   └── Development tools
└── 🎯 Orchestration: OpenSSL DevEnv (../openssl-devenv/)
    ├── MCP project orchestrator
    ├── Cross-repository coordination
    └── CI/CD automation
```

## 🏛️ DDD Layered Architecture

### Dependency Flow
```
Presentation (Apps) → Application (SSL/TLS) → Domain (Crypto) ← Infrastructure (Providers)
```

### Layer Responsibilities

#### 🔬 **Domain Layer (Crypto)**
- Core cryptographic algorithms (AES, SHA, RSA, ECC)
- FIPS-approved primitives and mathematical operations
- Algorithm implementations without external dependencies
- **Dependencies**: None (pure domain logic)

#### 🛡️ **Application Layer (SSL/TLS)**
- TLS/SSL protocol state machines and orchestration
- Certificate validation and security policy enforcement
- **Dependencies**: Domain Layer (via interfaces)

#### 🔧 **Infrastructure Layer (Providers)**
- FIPS module implementation and self-tests
- External service integrations (HSM, TPM)
- Repository implementations for key/certificate storage
- **Dependencies**: Application + Domain Layers

#### 📱 **Presentation Layer (Apps)**
- OpenSSL CLI commands and API interfaces
- Input validation and error message formatting
- **Dependencies**: Application Layer

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Run the full development setup (includes all dependencies)
Ctrl+Shift+P → "Tasks: Run Task" → "Workflow: Full Development Setup"
```

### 2. Development Workflow
```bash
# Quick development cycle (build → test → verify)
Ctrl+Shift+P → "Tasks: Run Task" → "Workflow: Quick Development Cycle"
```

### 3. Start Monitoring Dashboard
```bash
# Launch development monitoring dashboard
Ctrl+Shift+P → "Tasks: Run Task" → "Monitoring: Start Development Dashboard"
```

## 🐍 Python Environment Setup

The workspace uses Python virtual environment from `openssl-conan-base`:

```bash
# Activate environment
source ../openssl-conan-base/.venv/bin/activate

# Install additional development tools
pip install -r ../openssl-tools/requirements-dev.txt
```

## 🔧 Development Tools Integration

### MCP Orchestrator
- Cross-repository coordination
- Automated build orchestration
- FIPS compliance validation
- CI/CD pipeline management

### Testing Framework
- FIPS self-tests validation
- Cryptographic algorithm testing
- Integration testing across layers
- Performance benchmarking

### Monitoring Dashboard
- Real-time build status
- Test results visualization
- FIPS compliance monitoring
- Development metrics tracking

## 🧪 Testing Strategy

### FIPS Testing
```bash
# Run comprehensive FIPS test suite
python ../openssl-tools/scripts/run_tests.py --fips --comprehensive
```

### Crypto Algorithm Testing
```bash
# Run specific algorithm tests
ctest --test-dir build -R crypto_aes
```

### Integration Testing
```bash
# Test full SSL/TLS handshake
python ../openssl-tools/scripts/integration_tests.py --ssl-handshake
```

## 🐛 Debugging

### Launch Configurations

#### **Full FIPS Stack Debug**
- OpenSSL FIPS binary + MCP Orchestrator
- Complete end-to-end debugging

#### **Development Workflow Debug**
- Conan recipe creation + Testing tools + OpenSSL binary
- Full development cycle debugging

#### **Individual Component Debug**
- MCP Orchestrator only
- Testing tools only
- OpenSSL FIPS module only

### Environment Variables
```bash
# FIPS configuration
OPENSSL_FIPS=1
OPENSSL_CONF=./providers/fipsmodule.cnf
OPENSSL_MODULES=./build/providers

# Python path for tools
PYTHONPATH=../openssl-tools/scripts:../openssl-conan-base/src
```

## 📊 Build System

### CMake Presets
- `conan-debug`: Debug build with Conan dependencies
- `conan-release`: Release build with Conan dependencies
- `conan-release-fips-only`: FIPS-only release build

### Build Commands
```bash
# Configure
cmake --preset conan-debug -DOPENSSL_FIPS=ON

# Build
cmake --build build --config Debug

# Test
ctest --test-dir build
```

## 🔒 Security Considerations

### FIPS Compliance
- All cryptographic operations must use FIPS-approved algorithms
- Self-tests run automatically on module initialization
- FIPS boundaries clearly documented and validated
- Security audit logging enabled

### Development Security
- Virtual environment isolation
- Dependency vulnerability scanning
- Code signing for releases
- Secure credential management

## 🤝 Contributing

### Development Workflow
1. Create feature branch from `main`
2. Make changes following DDD layered architecture
3. Run full test suite locally
4. Submit pull request with FIPS compliance validation
5. Automated CI/CD pipeline validates changes

### Code Standards
- Follow OpenSSL coding conventions
- Use FIPS-compliant algorithms only
- Document security implications
- Include comprehensive test coverage

## 📚 Documentation

- **API Documentation**: Generated from source code comments
- **Security Documentation**: FIPS compliance and threat models
- **Architecture Documentation**: DDD layered architecture guides
- **Development Documentation**: Setup and contribution guides

## 🔧 Troubleshooting

### Common Issues

#### Python Environment
```bash
# Rebuild virtual environment
rm -rf ../openssl-conan-base/.venv
python ../openssl-conan-base/scripts/setup_environment.py --rebuild
```

#### Conan Cache Issues
```bash
# Clear Conan cache
conan remove "*" -c
conan install . --build=missing
```

#### FIPS Module Issues
```bash
# Reinstall FIPS module
openssl fipsinstall -out providers/fipsmodule.cnf -module build/providers/fips.so
```

#### Build Failures
```bash
# Clean rebuild
rm -rf build/
cmake --preset conan-debug
cmake --build build
```

## 📞 Support

- **Documentation**: See individual repository READMEs
- **Issues**: Create GitHub issues in appropriate repositories
- **Security**: security@openssl.org for security-related issues

---

**Note**: This workspace follows DDD principles to maintain clean separation of concerns while enabling efficient FIPS-compliant OpenSSL development across multiple repositories.
