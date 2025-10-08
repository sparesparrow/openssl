# Conan Development Environment

A comprehensive Python-based Conan development environment with automated CI/CD workflows.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Run the setup script
python scripts/setup-conan-dev-env.py

# Or use the quick setup
./scripts/conan/conan-dev-setup
```

### 2. Developer Commands
```bash
# Install dependencies
conan-install

# Build package
conan-build

# Build with specific profile
conan-build -p linux-clang15

# Build and test
conan-build -t

# Clean build
conan-build -c
```

## 📁 Directory Structure

```
conan-dev/
├── profiles/           # Conan profiles for different platforms
│   ├── linux-gcc11.profile
│   ├── linux-clang15.profile
│   ├── windows-msvc2022.profile
│   ├── macos-clang14.profile
│   └── debug.profile
├── locks/             # Lockfiles for reproducible builds
├── cache/             # Local cache directory
├── artifacts/         # Build artifacts
├── conan.conf         # Conan configuration
└── ci-config.yml      # CI/CD configuration

scripts/conan/
├── conan-install      # Install dependencies script
├── conan-build        # Build package script
├── conan-dev-setup    # Development setup script
└── performance_benchmark.py  # Performance testing

.github/workflows/
├── conan-ci.yml           # Branch compilation triggers
├── conan-pr-tests.yml     # PR integration tests
├── conan-release.yml      # Release & deployment
├── conan-manual-trigger.yml  # Manual triggers via comments
└── conan-nightly.yml      # Nightly rebuilds
```

## 🔄 CI/CD Workflows

### 1. Branch Compilation (`conan-ci.yml`)
**Triggers:** Push to any branch with changes to:
- `conanfile.py`, `conanfile.txt`
- `conan-recipes/**`
- `src/**`, `include/**`, `test/**`
- Build files (`CMakeLists.txt`, `Makefile`, `configure`)

**Actions:**
- Detects changed components (OpenSSL, Conan, Tests)
- Compiles affected code on Linux (GCC 11, Clang 15)
- Uploads build artifacts

### 2. PR Integration Tests (`conan-pr-tests.yml`)
**Triggers:** Pull requests to `main`/`master` branch

**Actions:**
- Multi-platform testing (Linux, Windows, macOS)
- Security scanning (Safety, Bandit)
- Performance benchmarking
- Lockfile generation
- Test result upload

### 3. Release & Deploy (`conan-release.yml`)
**Triggers:** 
- Push to `main`/`master` with version changes
- Manual workflow dispatch

**Actions:**
- Version detection and validation
- Multi-platform package building
- Production deployment
- GitHub release creation

### 4. Manual Triggers (`conan-manual-trigger.yml`)
**Triggers:**
- Issue comments with specific commands
- Manual workflow dispatch

**Commands:**
- `/conan build` - Build package
- `/conan test` - Run tests
- `/conan release` - Trigger release

**Example Comments:**
```
/conan build
/conan build linux-clang15
/conan test
/conan release
```

### 5. Nightly Rebuilds (`conan-nightly.yml`)
**Triggers:**
- Daily at 2 AM UTC
- Manual workflow dispatch

**Actions:**
- Identifies branches with recent changes
- Rebuilds packages for changed branches
- Runs comprehensive tests
- Cleans up old artifacts

## 🛠️ Available Profiles

| Profile | OS | Compiler | Architecture | Use Case |
|---------|----|---------|--------------|----------|
| `linux-gcc11` | Linux | GCC 11 | x86_64 | Primary development |
| `linux-clang15` | Linux | Clang 15 | x86_64 | Alternative compiler |
| `windows-msvc2022` | Windows | MSVC 2022 | x86_64 | Windows support |
| `macos-clang14` | macOS | Apple Clang 14 | x86_64 | macOS support |
| `debug` | Any | Any | Any | Debug builds |

## 📊 Performance Monitoring

### Benchmark Script
```bash
# Run benchmark for specific profile
python scripts/conan/performance_benchmark.py -p linux-gcc11

# Run benchmark for all profiles
python scripts/conan/performance_benchmark.py -a

# Generate report
python scripts/conan/performance_benchmark.py -a -r
```

### Metrics Tracked
- **Install Time**: Dependency resolution and installation
- **Build Time**: Package compilation
- **Test Time**: Test execution
- **Package Size**: Final package size
- **Total Time**: End-to-end process time

## 🔧 Configuration

### Conan Configuration (`conan-dev/conan.conf`)
```ini
[storage]
path = ~/.conan2/data

[remotes]
conancenter = https://center.conan.io

[tools]
cmake.cmaketoolchain:generator = Ninja
system.package_manager:mode = install
system.package_manager:sudo = True
```

### CI Configuration (`conan-dev/ci-config.yml`)
```yaml
profiles:
  - linux-gcc11
  - linux-clang15
  - windows-msvc2022
  - macos-clang14

test:
  coverage_threshold: 80
  timeout: 300

security:
  enabled: true
  tools:
    - safety
    - bandit
    - semgrep
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Profile Not Found
```bash
# Check available profiles
ls conan-dev/profiles/*.profile

# Create custom profile
conan profile new custom-profile --detect
```

#### 2. Build Failures
```bash
# Clean and rebuild
conan-build -c

# Verbose output
conan-build -v

# Check dependencies
conan install . --build=missing -v
```

#### 3. CI/CD Issues
- Check workflow permissions
- Verify secrets are configured
- Review workflow logs
- Ensure profiles exist

### Debug Commands
```bash
# Check Conan version
conan --version

# List profiles
conan profile list

# Check configuration
conan config list

# Verbose install
conan install . --build=missing -v
```

## 📈 Best Practices

### Development Workflow
1. **Start with**: `conan-install` to get dependencies
2. **Develop**: Make changes to source code
3. **Build**: `conan-build` to compile
4. **Test**: `conan-build -t` to run tests
5. **Commit**: Push changes to trigger CI

### CI/CD Best Practices
- Use lockfiles for reproducible builds
- Run tests on multiple platforms
- Monitor performance metrics
- Keep profiles up to date
- Use security scanning

### Performance Optimization
- Use `--build=missing` to avoid unnecessary rebuilds
- Enable parallel builds with `-j$(nproc)`
- Use binary packages when possible
- Monitor build times and optimize slow profiles

## 🔐 Security

### Automated Security Scanning
- **Safety**: Python dependency vulnerabilities
- **Bandit**: Python security issues
- **Semgrep**: Code security patterns

### Security Best Practices
- Regular dependency updates
- Vulnerability scanning in CI
- Secure package signing
- Access control for remotes

## 📚 Additional Resources

- [Conan Documentation](https://docs.conan.io/)
- [Conan 2.x Migration Guide](https://docs.conan.io/2.0/migrating_to_2.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OpenSSL Conan Package](https://conan.io/center/openssl)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test with `conan-build -t`
5. Submit a pull request

The CI/CD system will automatically:
- Run integration tests
- Perform security scans
- Generate performance reports
- Validate the changes

## 📞 Support

- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: Check this README and inline comments
- **CI/CD**: Review workflow logs for automation issues