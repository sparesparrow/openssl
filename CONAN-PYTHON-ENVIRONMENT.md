# Conan Python Environment

Cross-platform Python-based Conan development environment.

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
# Windows:
conan-install.bat
conan-build.bat

# Unix/Linux/macOS:
./conan-install
./conan-build
```

## 🖥️ Platform Support

### Windows
- **Launchers**: `.bat` files
- **Default Profile**: `windows-msvc2022`
- **Available Profiles**: `windows-msvc2022`, `debug`

### macOS
- **Launchers**: Shell scripts
- **Default Profile**: `macos-clang14`
- **Available Profiles**: `macos-clang14`, `debug`

### Linux
- **Launchers**: Shell scripts
- **Default Profile**: `linux-gcc11`
- **Available Profiles**: `linux-gcc11`, `linux-clang15`, `debug`

## 🔧 Python Orchestrator

The `conan_orchestrator.py` provides:
- Cross-platform profile management
- Virtual environment handling
- Platform detection
- Unified command interface

## 📁 Directory Structure

```
conan-dev/
├── profiles/           # Platform-specific profiles
├── venv/              # Python virtual environment
├── cache/             # Conan cache
├── artifacts/         # Build artifacts
└── platform-config.yml # Platform configuration

scripts/conan/
├── conan_orchestrator.py  # Core orchestrator
├── conan_cli.py          # Unified CLI
├── conan-install.py      # Install script
├── conan-build.py        # Build script
├── conan-dev-setup.py    # Setup script
├── conan-install.bat     # Windows launcher
├── conan-build.bat       # Windows launcher
├── conan-dev-setup.bat   # Windows launcher
├── conan-cli.bat         # Windows launcher
├── conan-install         # Unix launcher
├── conan-build           # Unix launcher
├── conan-dev-setup       # Unix launcher
└── conan-cli             # Unix launcher
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

### Platform-Specific Usage
```bash
# Windows
conan-install.bat -p windows-msvc2022
conan-build.bat -t

# macOS
./conan-install -p macos-clang14
./conan-build -t

# Linux
./conan-install -p linux-clang15
./conan-build -t
```

### Advanced Usage
```bash
# List available profiles
python scripts/conan/conan_cli.py list-profiles

# Show environment info
python scripts/conan/conan_cli.py info

# Verbose output
python scripts/conan/conan_cli.py build --verbose

# Clean build
python scripts/conan/conan_cli.py build --clean
```

## 🔄 CI/CD Integration

The CI/CD workflows have been updated to use Python orchestration:
- Cross-platform compatibility
- Unified command interface
- Better error handling
- Platform detection

## 🛠️ Troubleshooting

### Common Issues

#### 1. Python Not Found
```bash
# Check Python installation
python --version
python3 --version

# Use full path if needed
/path/to/python scripts/conan/conan_cli.py setup
```

#### 2. Permission Issues (Unix)
```bash
# Make scripts executable
chmod +x scripts/conan/conan-*
```

#### 3. Profile Not Found
```bash
# List available profiles
python scripts/conan/conan_cli.py list-profiles

# Check platform configuration
python scripts/conan/conan_cli.py info
```

### Debug Commands
```bash
# Verbose output
python scripts/conan/conan_cli.py build --verbose

# Environment info
python scripts/conan/conan_cli.py info

# List profiles
python scripts/conan/conan_cli.py list-profiles
```

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

## 🤝 Contributing

1. Fork the repository
2. Make changes to Python scripts
3. Test on multiple platforms
4. Submit a pull request

The Python orchestrator makes it easy to add new features and platforms.
