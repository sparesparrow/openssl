# OpenSSL Repository

This repository contains the core OpenSSL library implementation.

## Repository Cooperation

This repository works with [openssl-tools](https://github.com/sparesparrow/openssl-tools) for:
- Advanced CI/CD orchestration
- Conan package management
- Build optimization and caching
- Artifact distribution

## Development Workflow

1. Make changes to OpenSSL source code
2. Push changes (triggers core validation)
3. Core validation triggers openssl-tools CI
4. Packages built and distributed via openssl-tools

## Modern Package Management with Conan

This fork includes **minimal, upstream-friendly** Conan integration that enhances OpenSSL's usability in modern development environments while maintaining full compatibility with traditional build systems.

### Why Conan Integration?

**For Package Consumers:**
- **Zero-install usage**: `conan install openssl/4.0.0-dev@user/stable`
- **Cross-platform binaries**: Pre-built packages for Linux, Windows, macOS
- **Dependency management**: Automatic resolution of build dependencies
- **Reproducible builds**: Consistent environments across development and CI

**For Package Maintainers:**
- **Multi-platform CI**: Automated testing across compiler/OS combinations
- **Security scanning**: Integrated CodeQL, Trivy, and SBOM generation
- **Artifact distribution**: Automated publishing to package registries
- **Build optimization**: Intelligent caching and parallel builds

### Quick Start with Conan

```bash
# Install Conan (requires Python 3.6+)
pip install conan

# Clone and build
git clone https://github.com/sparesparrow/openssl.git
cd openssl

# Create package with default settings
conan create . --build missing

# Install for development
conan install . --build missing

# Test the package
conan test test_package
```

### Available Configurations

| Configuration | Profile | Description |
|---------------|---------|-------------|
| **Linux Release** | `linux-gcc-release` | Production Linux build, optimized |
| **Linux FIPS** | `linux-fips` | FIPS 140-3 compliant build |
| **Windows MSVC** | `windows-msvc` | Visual Studio 2022 build |
| **macOS Clang** | `macos-clang` | ARM64 optimized macOS build |

### Advanced Usage

```bash
# FIPS-compliant build
conan create . --profile=linux-fips

# Static linking
conan create . -o shared=False -o fPIC=True

# Custom build type
conan create . -s build_type=Debug

# Cross-platform from Linux
conan create . --profile:build linux-gcc-release --profile:host windows-msvc
```

### Integration with Build Systems

**CMake:**
```cmake
find_package(openssl REQUIRED)
target_link_libraries(myapp openssl::openssl)
```

**CMake with Conan:**
```bash
conan install openssl/4.0.0-dev@user/stable --output-folder=build --build missing
cd build && cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake
cmake --build .
```

### CI/CD Integration

The repository includes comprehensive CI/CD workflows:

- **conan-integration-test.yml**: Multi-platform package testing
- **codeql-analysis.yml**: Security vulnerability scanning
- **sbom-generation.yml**: Software Bill of Materials generation
- **Trivy integration**: Container and dependency scanning

### Migration from Traditional Builds

Existing projects can migrate gradually:

```bash
# Traditional build (unchanged)
./Configure --prefix=/usr/local
make && make install

# Conan build (new option)
conan create . --profile=linux-gcc-release

# Both can coexist during migration
```

See [BUILDING-CONAN.md](BUILDING-CONAN.md) for comprehensive migration guidance.

### Security and Compliance

- **FIPS 140-3**: Validated cryptographic module (Certificate #4985)
- **SBOM**: Automated Software Bill of Materials generation
- **Vulnerability scanning**: Trivy and CodeQL integration
- **Supply chain security**: Signed packages and audit trails

### Repository Architecture

This repository maintains **minimal changes** from upstream OpenSSL:

- Core cryptographic functionality: **100% upstream**
- Build system: **Traditional Configure/Make preserved**
- Package management: **Conan integration added**
- CI/CD: **Enhanced workflows added**

This approach ensures:
- ✅ Easy upstream merging
- ✅ Zero breaking changes
- ✅ Traditional build compatibility
- ✅ Modern package management benefits

### Contributing

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/conan-enhancement`)
3. **Make changes** (test with multiple profiles)
4. **Run tests**: `conan test test_package`
5. **Submit pull request**

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

*This is a fork of the official [OpenSSL project](https://github.com/openssl/openssl) with minimal changes to support Conan packaging.*

Welcome to the OpenSSL Project
==============================

[![openssl logo]][www.openssl.org]

OpenSSL is a robust, commercial-grade, full-featured Open Source Toolkit
for the TLS (formerly SSL), DTLS and QUIC protocols.

The protocol implementations are based on a full-strength general purpose
cryptographic library, which can also be used stand-alone. Also included is a
cryptographic module validated to conform with FIPS standards.

OpenSSL is descended from the SSLeay library developed by Eric A. Young
and Tim J. Hudson.

The official Home Page of the OpenSSL Project is [www.openssl.org].

Table of Contents
=================

 - [Overview](#overview)
 - [Download](#download)
 - [Build and Install](#build-and-install)
 - [Documentation](#documentation)
 - [License](#license)
 - [Support](#support)
 - [Contributing](#contributing)
 - [Legalities](#legalities)

Overview
========

The OpenSSL toolkit includes:

- **libssl**
  an implementation of all TLS protocol versions up to TLSv1.3 ([RFC 8446]),
  DTLS protocol versions up to DTLSv1.2 ([RFC 6347]) and
  the QUIC version 1 protocol ([RFC 9000]).

- **libcrypto**
  a full-strength general purpose cryptographic library. It constitutes the
  basis of the TLS implementation, but can also be used independently.

- **openssl**
  the OpenSSL command line tool, a swiss army knife for cryptographic tasks,
  testing and analyzing. It can be used for
  - creation of key parameters
  - creation of X.509 certificates, CSRs and CRLs
  - calculation of message digests
  - encryption and decryption
  - SSL/TLS/DTLS and client and server tests
  - QUIC client tests
  - handling of S/MIME signed or encrypted mail
  - and more...

Download
========

For Production Use
------------------

Source code tarballs of the official releases can be downloaded from
[openssl-library.org/source/](https://openssl-library.org/source/).
The OpenSSL project does not distribute the toolkit in binary form.

However, for a large variety of operating systems precompiled versions
of the OpenSSL toolkit are available. In particular, on Linux and other
Unix operating systems, it is normally recommended to link against the
precompiled shared libraries provided by the distributor or vendor.

We also maintain a list of third parties that produce OpenSSL binaries for
various Operating Systems (including Windows) on the [Binaries] page on our
wiki.

For Testing and Development
---------------------------

Although testing and development could in theory also be done using
the source tarballs, having a local copy of the git repository with
the entire project history gives you much more insight into the
code base.

The main OpenSSL Git repository is private.
There is a public GitHub mirror of it at [github.com/openssl/openssl],
which is updated automatically from the former on every commit.

A local copy of the Git repository can be obtained by cloning it from
the GitHub mirror using

    git clone https://github.com/openssl/openssl.git

If you intend to contribute to OpenSSL, either to fix bugs or contribute
new features, you need to fork the GitHub mirror and clone your public fork
instead.

    git clone https://github.com/yourname/openssl.git

This is necessary because all development of OpenSSL nowadays is done via
GitHub pull requests. For more details, see [Contributing](#contributing).

Build and Install
=================

After obtaining the Source, have a look at the [INSTALL](INSTALL.md) file for
detailed instructions about building and installing OpenSSL. For some
platforms, the installation instructions are amended by a platform specific
document.

 * [Notes for UNIX-like platforms](NOTES-UNIX.md)
 * [Notes for Android platforms](NOTES-ANDROID.md)
 * [Notes for Windows platforms](NOTES-WINDOWS.md)
 * [Notes for the DOS platform with DJGPP](NOTES-DJGPP.md)
 * [Notes for the OpenVMS platform](NOTES-VMS.md)
 * [Notes on Perl](NOTES-PERL.md)
 * [Notes on Valgrind](NOTES-VALGRIND.md)

Specific notes on upgrading to OpenSSL 3.x from previous versions can be found
in the [ossl-guide-migration(7ossl)] manual page.

Documentation
=============

README Files
------------

There are some README.md files in the top level of the source distribution
containing additional information on specific topics.

 * [Information about the OpenSSL QUIC protocol implementation](README-QUIC.md)
 * [Information about the OpenSSL Provider architecture](README-PROVIDERS.md)
 * [Information about using the OpenSSL FIPS validated module](README-FIPS.md)
 * [Information about the legacy OpenSSL Engine architecture](README-ENGINES.md)

The OpenSSL Guide
-----------------

There are some tutorial and introductory pages on some important OpenSSL topics
within the [OpenSSL Guide].

Manual Pages
------------

The manual pages for the master branch and all current stable releases are
available online.

- [OpenSSL master](https://docs.openssl.org/master/)
- [OpenSSL 3.5](https://docs.openssl.org/3.5/)
- [OpenSSL 3.4](https://docs.openssl.org/3.4/)
- [OpenSSL 3.3](https://docs.openssl.org/3.3/)
- [OpenSSL 3.2](https://docs.openssl.org/3.2/)
- [OpenSSL 3.0](https://docs.openssl.org/3.0/)

Demos
-----

There are numerous source code demos for using various OpenSSL capabilities in the
[demos subfolder](./demos).

Wiki
----

There is a [GitHub Wiki] which is currently not very active.

License
=======

OpenSSL is licensed under the Apache License 2.0, which means that
you are free to get and use it for commercial and non-commercial
purposes as long as you fulfill its conditions.

See the [LICENSE.txt](LICENSE.txt) file for more details.

Support
=======

There are various ways to get in touch. The correct channel depends on
your requirement. See the [SUPPORT](SUPPORT.md) file for more details.

Contributing
============

If you are interested and willing to contribute to the OpenSSL project,
please take a look at the [CONTRIBUTING](CONTRIBUTING.md) file.

Legalities
==========

A number of nations restrict the use or export of cryptography. If you are
potentially subject to such restrictions, you should seek legal advice before
attempting to develop or distribute cryptographic code.

Copyright
=========

Copyright (c) 1998-2025 The OpenSSL Project Authors

Copyright (c) 1995-1998 Eric A. Young, Tim J. Hudson

All rights reserved.

<!-- Links  -->

[www.openssl.org]:
    <https://www.openssl.org>
    "OpenSSL Homepage"

[github.com/openssl/openssl]:
    <https://github.com/openssl/openssl>
    "OpenSSL GitHub Mirror"

[GitHub Wiki]:
    <https://github.com/openssl/openssl/wiki>
    "OpenSSL Wiki"

[ossl-guide-migration(7ossl)]:
    <https://docs.openssl.org/master/man7/ossl-guide-migration>
    "OpenSSL Migration Guide"

[RFC 8446]:
     <https://tools.ietf.org/html/rfc8446>

[RFC 6347]:
     <https://tools.ietf.org/html/rfc6347>

[RFC 9000]:
     <https://tools.ietf.org/html/rfc9000>

[Binaries]:
    <https://github.com/openssl/openssl/wiki/Binaries>
    "List of third party OpenSSL binaries"

[OpenSSL Guide]:
    <https://docs.openssl.org/master/man7/ossl-guide-introduction>
    "An introduction to OpenSSL"

<!-- Logos and Badges -->

[openssl logo]:
    doc/images/openssl.svg
    "OpenSSL Logo"

[github actions ci badge]:
    <https://github.com/openssl/openssl/workflows/GitHub%20CI/badge.svg>
    "GitHub Actions CI Status"

[github actions ci]:
    <https://github.com/openssl/openssl/actions/workflows/ci.yml>
    "GitHub Actions CI"

[appveyor badge]:
    <https://ci.appveyor.com/api/projects/status/8e10o7xfrg73v98f/branch/master?svg=true>
    "AppVeyor Build Status"

[appveyor jobs]:
    <https://ci.appveyor.com/project/openssl/openssl/branch/master>
    "AppVeyor Jobs"
# Test trigger - Fri Oct 10 02:51:19 AM CEST 2025
# Test dispatch token
