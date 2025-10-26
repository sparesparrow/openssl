---
description: OpenSSL-specific operations and workflows for building, testing, and deploying components
globs: ["openssl-*/**", "scripts/**", "conanfile.py", "*.sh"]
alwaysApply: true
category: "OpenSSL Commands"
version: "1.0.0"
---

# OpenSSL Commands

OpenSSL-specific operations and workflows for building, testing, and deploying components.

## Build Commands

### 🔨 Build All Components
- **ID**: `openssl.build-all`
- **Description**: Build all OpenSSL components with database tracking
- **Command**: `./scripts/build/build-all-components.sh`
- **Category**: Build
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+B`

### ⚡ Quick Build
- **ID**: `openssl.quick-build`
- **Description**: Fast build with cached dependencies
- **Command**: `./scripts/build/build-components-no-db.sh`
- **Category**: Build
- **Group**: openssl
- **Shortcut**: `Ctrl+Q+B`

## Conan Extension Commands

### 🔧 Configure OpenSSL
- **ID**: `openssl.conan-configure`
- **Description**: Configure OpenSSL build environment with Conan integration
- **Command**: `conan openssl configure --profile=ci-linux-gcc --verbose`
- **Category**: Conan
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+C`

### 🏗️ Build OpenSSL
- **ID**: `openssl.conan-build`
- **Description**: Build OpenSSL with Conan integration and database tracking
- **Command**: `conan openssl build --profile=ci-linux-gcc --test --verbose`
- **Category**: Conan
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+B`

### 📦 Package OpenSSL
- **ID**: `openssl.conan-package`
- **Description**: Package OpenSSL with SBOM generation and metadata
- **Command**: `conan openssl package --sbom --sbom-format=cyclonedx --verbose`
- **Category**: Conan
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+P`

### 📚 Generate Documentation
- **ID**: `openssl.conan-docs`
- **Description**: Generate and format OpenSSL documentation from sources
- **Command**: `conan openssl docs --format=html --sections=all --verbose`
- **Category**: Conan
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+D`

### 🏃 Run Benchmarks
- **ID**: `openssl.conan-benchmark`
- **Description**: Run performance benchmarks and generate reports
- **Command**: `conan openssl benchmark --benchmarks=all --iterations=1000 --format=json --verbose`
- **Category**: Conan
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+M`

### 🔍 Security Scan
- **ID**: `openssl.conan-scan`
- **Description**: Execute comprehensive security scans (SAST/DAST)
- **Command**: `conan openssl scan --scan-types=all --tools=all --severity=medium --verbose`
- **Category**: Conan
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+S`

## Distribution Commands

### 📦 Upload to Registries
- **ID**: `openssl.upload-registries`
- **Description**: Upload all components to configured registries
- **Command**: `./scripts/upload/upload-to-registries.sh`
- **Category**: Distribution
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+U`

### 🚀 Deploy to Production
- **ID**: `openssl.deploy-production`
- **Description**: Deploy components to production registry
- **Command**: `./scripts/deployment/deploy-production.sh`
- **Category**: Deployment
- **Group**: openssl
- **Confirmation**: "Are you sure you want to deploy to production?"

## Database Commands

### 🐘 Database Status
- **ID**: `openssl.db-status`
- **Description**: Show recent build status from database
- **Command**: Shows last 10 builds with component names, status, and dates
- **Category**: Database
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+D`

### 💾 Database Backup
- **ID**: `openssl.db-backup`
- **Description**: Create database backup
- **Command**: `./scripts/database/backup-database.sh`
- **Category**: Maintenance
- **Group**: openssl

## Testing Commands

### 🧪 Test Component
- **ID**: `openssl.test-component`
- **Description**: Test a specific component
- **Command**: `./scripts/testing/test-component.sh`
- **Category**: Testing
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+T`
- **Prompt**: "Which component to test? (crypto/ssl/tools)"

### 🧪 Quick Test
- **ID**: `openssl.quick-test`
- **Description**: Run basic component tests
- **Command**: `./scripts/testing/quick-test.sh`
- **Category**: Testing
- **Group**: openssl
- **Shortcut**: `Ctrl+Q+T`

### 📊 Performance Benchmark
- **ID**: `openssl.benchmark`
- **Description**: Run performance benchmarks
- **Command**: `./scripts/testing/run-benchmarks.sh`
- **Category**: Testing
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+P`

## Security Commands

### 🔒 Security Scan
- **ID**: `openssl.security-scan`
- **Description**: Run security analysis on all components
- **Command**: `./scripts/security/run-security-scan.sh`
- **Category**: Security
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+S`

## Maintenance Commands

### 🧹 Clean Build Cache
- **ID**: `openssl.clean-cache`
- **Description**: Clean Conan cache and restart fresh
- **Command**: `conan remove '*' -f && echo 'Cache cleaned successfully'`
- **Category**: Maintenance
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+C`

## Reporting Commands

### 📋 Generate Report
- **ID**: `openssl.generate-report`
- **Description**: Generate comprehensive pipeline report
- **Command**: `./scripts/reporting/generate-pipeline-report.sh`
- **Category**: Reporting
- **Group**: openssl
- **Shortcut**: `Ctrl+Shift+R`

### 📊 Quick Status
- **ID**: `openssl.quick-status`
- **Description**: Show pipeline status summary
- **Command**: Shows Docker containers and Conan package status
- **Category**: Status
- **Group**: openssl
- **Shortcut**: `Ctrl+Q+S`

## Context Menus

### Conanfile.py Actions
Right-click on `conanfile.py` files to access:

#### Create Package
- **ID**: `conanfile.create-package`
- **Description**: Create package from current conanfile.py
- **Command**: `conan create . --profile:build=default --profile:host=default -s build_type=Release`

#### Test Package
- **ID**: `conanfile.test-package`
- **Description**: Test package using test_package
- **Command**: `conan test test_package . --profile:build=default --profile:host=default`

### Shell Script Actions
Right-click on `*.sh` files to access:

#### Make Executable
- **ID**: `shell.make-executable`
- **Description**: Make shell script executable
- **Command**: `chmod +x {{file}}`

#### Run Script
- **ID**: `shell.run-script`
- **Description**: Execute shell script
- **Command**: `./{{file}}`

## Usage

### In Cursor IDE
1. Open Command Palette (`Ctrl+Shift+P`)
2. Type command ID (e.g., `openssl.build-all`)
3. Execute with Enter

### Keyboard Shortcuts
- **`Ctrl+Shift+B`**: Build All Components
- **`Ctrl+Shift+U`**: Upload to Registries
- **`Ctrl+Shift+D`**: Database Status
- **`Ctrl+Shift+C`**: Clean Build Cache
- **`Ctrl+Shift+S`**: Security Scan
- **`Ctrl+Shift+P`**: Performance Benchmark
- **`Ctrl+Shift+R`**: Generate Report
- **`Ctrl+Shift+T`**: Test Component
- **`Ctrl+Q+B`**: Quick Build
- **`Ctrl+Q+T`**: Quick Test
- **`Ctrl+Q+S`**: Quick Status

### Context Menus
Right-click on files to access context-specific commands:
- **conanfile.py**: Create Package, Test Package
- ***.sh**: Make Executable, Run Script

## Workflow Examples

### Development Workflow
1. **Quick Status**: Check current state with `Ctrl+Q+S`
2. **Quick Build**: Fast build with `Ctrl+Q+B`
3. **Quick Test**: Test changes with `Ctrl+Q+T`
4. **Generate Report**: Create status report with `Ctrl+Shift+R`

### Production Workflow
1. **Build All**: Full build with `Ctrl+Shift+B`
2. **Security Scan**: Check security with `Ctrl+Shift+S`
3. **Performance Test**: Benchmark with `Ctrl+Shift+P`
4. **Deploy**: Production deployment with confirmation

### Maintenance Workflow
1. **Database Backup**: Backup with `openssl.db-backup`
2. **Clean Cache**: Fresh start with `Ctrl+Shift+C`
3. **Database Status**: Check status with `Ctrl+Shift+D`

## Environment Requirements
- Docker and Docker Compose
- Conan 2.x configured
- PostgreSQL database
- Required scripts in place
- Proper profiles configured

## Troubleshooting

### Build Issues
- Check database is running
- Verify Conan profiles
- Use `Ctrl+Shift+C` for clean start
- Check script permissions

### Testing Issues
- Ensure components are built
- Check test scripts exist
- Verify database connectivity
- Review test configurations

### Deployment Issues
- Verify registry configuration
- Check authentication
- Ensure components are built
- Review deployment scripts
