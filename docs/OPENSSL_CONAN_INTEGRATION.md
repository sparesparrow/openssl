# OpenSSL Conan Integration

This document describes the advanced Conan scripts for the OpenSSL project, providing comprehensive package management and build automation capabilities.

## Overview

The OpenSSL Conan integration provides a comprehensive set of tools for managing Conan packages, Artifactory remotes, and build automation specifically tailored for OpenSSL development. This integration is based on proven patterns and adapted for OpenSSL's specific needs.

## Features

- **Advanced Package Management**: Comprehensive package discovery, installation, and management
- **Artifactory Integration**: Support for multiple Conan remotes and Artifactory repositories
- **Configuration Tracking**: Track package usage and manage cache efficiently
- **Build Automation**: Automated build processes with parallel execution
- **Security Scanning**: Built-in security and vulnerability checking
- **CI/CD Integration**: Ready for continuous integration and deployment

## Directory Structure

```
scripts/openssl_conan/conan/
├── __init__.py                    # Module initialization
├── conan_functions.py            # Core Conan functionality
├── artifactory_functions.py      # Artifactory integration
├── client_config.py              # Configuration management
├── conan_artifactory_search.py   # Package search and discovery
├── pyupdater_downloader.py       # File download utilities
├── test_conan_functions.py       # Unit tests for Conan functions
├── test_artifactory_functions.py # Unit tests for Artifactory functions
└── openssl_conan_example.py      # Usage examples
```

## Core Components

### 1. Conan Functions (`conan_functions.py`)

The core functionality for Conan package management:

#### Key Classes

- **`ConanConfiguration`**: Manages Conan configurations and package tracking
- **`ConanConfigurationTracker`**: Tracks package usage and manages cache
- **`ConanJsonLoader`**: Loads and parses Conan JSON information

#### Key Functions

- **`get_default_conan()`**: Get the default Conan executable path
- **`get_conan_home()`**: Get Conan home directory
- **`install_packages_for_repository()`**: Install packages for a repository
- **`download_package_for_repository()`**: Download specific packages
- **`create_package_graph()`**: Create dependency graphs
- **`setup_parallel_download()`**: Configure parallel downloads

#### Usage Example

```python
from openssl_conan.conan.conan_functions import (
    get_default_conan,
    install_packages_for_repository,
    create_package_graph
)

# Get Conan executable
conan_exe = get_default_conan()

# Install packages for current repository
packages = install_packages_for_repository('.')

# Create dependency graph
graph_file = create_package_graph('.')
```

### 2. Artifactory Functions (`artifactory_functions.py`)

Integration with Artifactory and Conan remotes:

#### Key Functions

- **`setup_artifactory_remote()`**: Set up Artifactory remote
- **`configure_artifactory_for_openssl()`**: Configure for OpenSSL project
- **`search_packages_in_remote()`**: Search packages in specific remote
- **`upload_package_to_remote()`**: Upload packages to remote
- **`setup_openssl_remotes()`**: Set up OpenSSL-specific remotes

#### Usage Example

```python
from openssl_conan.conan.artifactory_functions import (
    setup_artifactory_remote,
    search_packages_in_remote,
    setup_openssl_remotes
)

# Set up remotes
setup_openssl_remotes()

# Search for OpenSSL packages
results = search_packages_in_remote('conancenter', 'openssl/*')
```

### 3. Client Configuration (`client_config.py`)

Configuration management for the OpenSSL Conan integration:

#### Key Features

- Environment variable management
- Build option configuration
- Security settings
- Cache management
- Logging configuration

#### Usage Example

```python
from openssl_conan.conan.client_config import get_client_config, setup_openssl_environment

# Get configuration
config = get_client_config()
config.print_config()

# Setup environment
setup_openssl_environment()
```

### 4. Package Search (`conan_artifactory_search.py`)

Advanced package search and discovery:

#### Key Functions

- **`search_package_pattern()`**: Search packages by pattern
- **`get_latest_package()`**: Get latest package version
- **`search_openssl_packages()`**: Search for OpenSSL packages
- **`update_conanfile_with_latest_packages()`**: Update conanfile.py with latest versions

#### Usage Example

```python
from openssl_conan.conan.conan_artifactory_search import (
    search_openssl_packages,
    get_latest_package
)

# Search for OpenSSL packages
search_openssl_packages()

# Get latest version
latest = get_latest_package('openssl', '3.*')
```

## Configuration

### Environment Variables

The integration uses several environment variables for configuration:

```bash
# Conan settings
export CONAN_USER_HOME="/path/to/conan/home"
export CONAN_REMOTE_NAME="conancenter"
export CONAN_REMOTE_URL="https://center.conan.io"
export CONAN_USER="username"
export CONAN_PASSWORD="password"

# OpenSSL settings
export OPENSSL_VERSION="3.5.0"
export OPENSSL_BUILD_TYPE="Release"
export OPENSSL_FIPS="True"
export OPENSSL_DEMOS="True"

# Build settings
export CONAN_CPU_COUNT="4"
export CONAN_ENABLE_CACHE="True"
export CONAN_LOG_LEVEL="INFO"
export CONAN_VERBOSE="False"

# Security settings
export CONAN_SECURITY_SCAN="True"
export CONAN_VULNERABILITY_CHECK="True"
```

### Configuration File

The integration automatically creates a configuration file at `~/.conan2/conan_tracker.yaml` to track package usage and manage cache.

## Usage Examples

### Basic Setup

```python
#!/usr/bin/env python3
from openssl_conan.conan.client_config import setup_openssl_environment
from openssl_conan.conan.artifactory_functions import configure_artifactory_for_openssl

# Setup environment
setup_openssl_environment()

# Configure Artifactory
configure_artifactory_for_openssl()
```

### Package Management

```python
#!/usr/bin/env python3
from openssl_conan.conan.conan_functions import (
    install_packages_for_repository,
    download_package_for_repository,
    create_package_graph
)

# Install packages
packages = install_packages_for_repository('.')

# Download specific package
package_path = download_package_for_repository('.', 'openssl')

# Create dependency graph
graph_file = create_package_graph('.')
```

### Package Search and Discovery

```python
#!/usr/bin/env python3
from openssl_conan.conan.conan_artifactory_search import (
    search_openssl_packages,
    get_latest_package,
    search_packages_by_keyword
)

# Search for OpenSSL packages
search_openssl_packages()

# Get latest version
latest = get_latest_package('openssl', '3.*')

# Search by keyword
search_packages_by_keyword('crypto')
```

### Remote Management

```python
#!/usr/bin/env python3
from openssl_conan.conan.artifactory_functions import (
    setup_openssl_remotes,
    search_packages_in_remote,
    upload_package_to_remote
)

# Setup remotes
setup_openssl_remotes()

# Search in specific remote
results = search_packages_in_remote('conancenter', 'openssl/*')

# Upload package
success = upload_package_to_remote('openssl/3.5.0', 'conancenter')
```

## Testing

The integration includes comprehensive unit tests:

```bash
# Run all tests
python -m pytest scripts/openssl_conan/conan/test_*.py -v

# Run specific test file
python scripts/openssl_conan/conan/test_conan_functions.py

# Run with coverage
python -m pytest scripts/openssl_conan/conan/test_*.py --cov=openssl_conan.conan --cov-report=html
```

## Integration with OpenSSL Build System

### Conanfile.py Integration

The OpenSSL Conan integration works seamlessly with the existing OpenSSL `conanfile.py`:

```python
# In conanfile.py
from openssl_conan.conan.conan_functions import get_default_conan

class OpenSSLConan(ConanFile):
    # ... existing configuration ...
    
    def build(self):
        # Use ngapy Conan functions
        conan_exe = get_default_conan()
        # ... build process ...
```

### CI/CD Integration

The integration provides ready-to-use functions for CI/CD pipelines:

```python
# In CI/CD script
from openssl_conan.conan.artifactory_functions import configure_for_ci_environment
from openssl_conan.conan.conan_functions import setup_parallel_download

# Configure for CI
configure_for_ci_environment()

# Setup parallel downloads
setup_parallel_download()
```

## Advanced Features

### Package Tracking

The integration automatically tracks package usage and can clean up old packages:

```python
from openssl_conan.conan.conan_functions import ConanConfigurationTracker
from datetime import timedelta

tracker = ConanConfigurationTracker()

# Remove packages older than 30 days
tracker.remove_old_packages(timedelta(days=30))
```

### Security Scanning

Built-in security and vulnerability checking:

```python
from ngapy.conan.client_config import get_client_config

config = get_client_config()
if config.ENABLE_SECURITY_SCAN:
    # Perform security scan
    pass
```

### Cache Management

Intelligent cache management:

```python
from openssl_conan.conan.conan_functions import remove_conan_lock_files

# Remove lock files
remove_conan_lock_files()
```

## Troubleshooting

### Common Issues

1. **Conan executable not found**
   - Ensure Conan is installed and in PATH
   - Check `get_default_conan()` function

2. **Remote connection issues**
   - Verify network connectivity
   - Check remote URLs and credentials

3. **Package installation failures**
   - Check package availability in remotes
   - Verify package versions and dependencies

4. **Cache issues**
   - Clear Conan cache: `conan remove "*" --force`
   - Remove lock files: `remove_conan_lock_files()`

### Debug Mode

Enable debug mode for detailed logging:

```bash
export CONAN_LOG_LEVEL="DEBUG"
export CONAN_VERBOSE="True"
```

## Contributing

When contributing to the ngapy Conan integration:

1. Follow the existing code style and patterns
2. Add comprehensive tests for new functionality
3. Update documentation for new features
4. Ensure compatibility with existing OpenSSL build system

## License

This integration is part of the OpenSSL project and follows the same licensing terms.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the test files for usage examples
3. Create an issue in the OpenSSL project repository
4. Consult the Conan documentation for general Conan issues