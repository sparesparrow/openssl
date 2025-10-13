# OpenSSL with Conan Packaging

OpenSSL cryptographic library with aerospace-quality build process.

## Deployment Targets

- **general** (default): Standard TLS/SSL applications
- **fips-government**: FIPS 140-3 validated (Certificate #4985)  
- **embedded**: Optimized for embedded systems

## Usage

```bash
# Add Cloudsmith remote
conan remote add sparesparrow-conan \
  https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

# Standard build
conan install --requires=openssl/3.4.1 -r=sparesparrow-conan

# FIPS government build  
conan install --requires=openssl/3.4.1 \
  -r=sparesparrow-conan \
  -o deployment_target=fips-government
```

## Build Process

```mermaid
graph LR
    A[Source Prep] --> B[Configure]
    B --> C[Build]
    C --> D[Test]
    D --> E[FIPS Validation]
    E --> F[Package]
```

## Dependencies

- openssl-build-tools/1.2.0 (tooling)
- openssl-fips-data/140-3.1 (FIPS compliance)
