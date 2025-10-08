# OpenSSL Python Environment Packaging

This document describes how to build and distribute Python environment packages for OpenSSL development using Conan and Artifactory.

## Overview

The OpenSSL project provides pre-built Python environment packages that include:
- Python runtime (3.8-3.13)
- Conan package manager
- Development tools (black, flake8, pylint, mypy, isort)
- Testing tools (pytest, pytest-cov, coverage)
- OpenSSL integration scripts

## Workflows

### 1. Automated Packaging (`python-environment-package.yml`)

This workflow automatically builds and packages Python environments when:
- Changes are made to Python-related scripts
- Triggered manually via workflow_dispatch

**Features:**
- Multi-platform builds (Linux, Windows, macOS)
- Automatic versioning based on date and commit
- Upload to Conan Center and Artifactory
- GitHub release creation

### 2. Manual Artifactory Upload (`upload-python-env-to-artifactory.yml`)

This workflow allows manual creation and upload of Python environment packages to Artifactory.

**Usage:**
1. Go to Actions → "Upload Python Environment to Artifactory"
2. Click "Run workflow"
3. Fill in the parameters:
   - Python version (default: 3.12)
   - Package version (default: latest)
   - Artifactory repository name
   - Include development tools (default: true)
   - Include testing tools (default: true)

### 3. Local Build Script (`scripts/build-python-environment.py`)

A Python script for building and uploading packages locally.

**Usage:**
```bash
# Basic build and upload
python scripts/build-python-environment.py

# Custom version and profile
python scripts/build-python-environment.py --python-version 3.11 --package-version 20241201.abc123

# Upload to Artifactory
python scripts/build-python-environment.py \
  --artifactory-url https://your-artifactory.com \
  --artifactory-username your-username \
  --artifactory-password your-password \
  --artifactory-repo conan-local

# Build only (no upload)
python scripts/build-python-environment.py --build-only
```

## Package Structure

The generated Python environment package includes:

```
openssl-python-environment/
├── bin/
│   └── setup_environment.py    # Main setup script
├── scripts/
│   └── openssl_conan/          # OpenSSL Conan integration scripts
├── conan-dev/
│   └── profiles/               # Conan profiles
├── README.md                   # Package documentation
└── requirements.txt            # Python requirements
```

## Installation

### From Conan Center
```bash
conan install openssl-python-environment/latest@openssl/stable
python bin/setup_environment.py
```

### From Artifactory
```bash
# Add Artifactory remote
conan remote add artifactory https://your-artifactory.com/conan-local

# Install package
conan install openssl-python-environment/latest@openssl/stable -r artifactory

# Set up environment
python bin/setup_environment.py
```

## Configuration

### Required Secrets

For Artifactory integration, set these GitHub secrets:

- `ARTIFACTORY_URL`: Your Artifactory instance URL
- `ARTIFACTORY_USERNAME`: Artifactory username
- `ARTIFACTORY_PASSWORD`: Artifactory password/token

### Environment Variables

The package sets these environment variables:
- `PYTHON_APPLICATION`: Path to Python executable
- `CONAN_COLOR_DISPLAY`: Enable colored Conan output
- `CLICOLOR_FORCE`: Force colored output
- `CLICOLOR`: Enable colored output

## Package Options

The Python environment package supports these options:

- `python_version`: Python version (3.8, 3.9, 3.10, 3.11, 3.12, 3.13)
- `include_dev_tools`: Include development tools (black, flake8, etc.)
- `include_testing`: Include testing tools (pytest, pytest-cov, etc.)

## Development

### Adding New Tools

To add new tools to the Python environment:

1. Update the `requirements` list in the Conan recipe
2. Update the `requirements.txt` generation
3. Update the setup script if needed

### Custom Profiles

To include custom Conan profiles:

1. Add profiles to `conan-dev/profiles/`
2. The build script will automatically include them

### Testing

Test the package locally:

```bash
# Build package
python scripts/build-python-environment.py --build-only

# Test installation
conan install openssl-python-environment/latest@openssl/stable --build=missing
python bin/setup_environment.py
```

## Troubleshooting

### Common Issues

1. **Build fails with missing dependencies**
   - Ensure all required Conan profiles exist
   - Check that Conan is properly configured

2. **Upload fails to Artifactory**
   - Verify Artifactory URL and credentials
   - Check repository permissions

3. **Package installation fails**
   - Ensure Conan remote is configured correctly
   - Check package version exists

### Debug Mode

Enable debug output:

```bash
export CONAN_LOGGING_LEVEL=10
python scripts/build-python-environment.py
```

## Best Practices

1. **Version Management**
   - Use semantic versioning for releases
   - Use date-based versioning for development builds

2. **Testing**
   - Test packages on multiple platforms
   - Verify all tools work correctly after installation

3. **Documentation**
   - Keep README.md up to date
   - Document any new tools or features

4. **Security**
   - Use secure credentials for Artifactory
   - Regularly rotate access tokens

## Support

For issues with Python environment packaging:

1. Check the GitHub Actions logs
2. Review the Conan build output
3. Test locally with the build script
4. Create an issue in the OpenSSL repository