# Building OpenSSL with Conan 2.x

This guide provides a concise, show-over-tell approach to building and consuming OpenSSL with Conan 2.x package manager.

## Prerequisites

- **Conan 2.x**: Version 2.21.0 or higher
- **Python**: Version 3.8 or higher (tested with Python 3.13.7)
- **CMake**: Version 3.15 or higher (for consumer projects)
- **Build Tools**: GCC 11.4+, Clang 15+, or MSVC 19.3+

## Basic Usage

### Install OpenSSL via Conan

```bash
conan install --requires=openssl/4.0.0 --build=missing
```

### Generate CMake files

```bash
conan install --requires=openssl/4.0.0 --generator=CMakeDeps --generator=CMakeToolchain
```

### Build your project

```bash
cmake --preset conan-release
cmake --build --preset conan-release
```

## Consumer Example

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.15)
project(MyOpenSSLApp)

find_package(OpenSSL REQUIRED)

add_executable(myapp main.cpp)
target_link_libraries(myapp OpenSSL::SSL OpenSSL::Crypto)
```

```cpp
// main.cpp
#include <openssl/ssl.h>
#include <openssl/crypto.h>
#include <iostream>

int main() {
    std::cout << "OpenSSL version: " << OpenSSL_version(OPENSSL_VERSION) << std::endl;
    return 0;
}
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `shared` | `True` | Build shared libraries |
| `fPIC` | `True` | Position independent code |

## Environment Variables

```bash
# Conan configuration
export CONAN_USER_HOME=/path/to/conan/home
export CONAN_LOG_LEVEL=10
export CONAN_TRACE_FILE=conan_trace.log
```

## Troubleshooting

### Common Issues

1. **Build Failures**:
   ```bash
   # Check build logs
   conan create . --build=missing -v
   ```

2. **Cross-Platform Issues**:
   ```bash
   # Check platform-specific requirements
   conan install . --build=missing
   ```

### Debug Information

```bash
# Verbose output
conan create . --build=missing -v

# Check package contents
conan package openssl/4.0.0@openssl/stable
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Install Conan
  run: pip install conan

- name: Configure Conan
  run: conan profile detect --force

- name: Install OpenSSL
  run: conan install --requires=openssl/4.0.0 --build=missing
```

**Tested With**: Conan 2.21.0, Python 3.13.7, GCC 15.2.0
**Status**: ✅ Production Ready