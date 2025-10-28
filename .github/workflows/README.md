# OpenSSL Fork - Workflow Organization

This directory contains the organized CI/CD workflows for the OpenSSL fork, structured for maintainability and clarity.

## Directory Structure

### `/core/` - Essential CI Workflows (4 workflows)
Core build and integration workflows that are essential for the OpenSSL fork:

- **`basic-openssl-build.yml`** - Custom OpenSSL build logic with Conan integration
- **`basic-openssl-integration.yml`** - Integration tests for OpenSSL builds
- **`fast-lane-ci.yml`** - Quick validation for bugfixes and small changes
- **`openssl-core-ci.yml`** - Core CI validation for OpenSSL source changes

### `/validation/` - PR Validation Workflows (3 workflows)
Workflows focused on validating pull requests and code quality:

- **`basic-validation.yml`** - Minimal validation for separated OpenSSL repository
- **`pr-validation.yml`** - Fast validation for pull requests (3-5 min)
- **`lightweight-check.yml`** - Lightweight checks for non-master branches

### `/release/` - Release Management Workflows (2 workflows)
Workflows for package release and deployment:

- **`conan-integration-test.yml`** - Conan package integration testing
- **`sbom-generation.yml`** - Software Bill of Materials generation

### `/maintenance/` - Maintenance Workflows (1 workflow)
Workflows for repository maintenance and upstream synchronization:

- **`upstream-sync.yml`** - Daily synchronization with upstream OpenSSL

### `/archive/` - Archived Workflows
Directory for moved or deprecated workflows (currently empty).

## Root Level Workflows

- **`codeql-analysis.yml`** - Security analysis using GitHub CodeQL

## Workflow Standards

All workflows follow these standards:

1. **Modern Actions**: Use `actions/checkout@v4`, `actions/setup-python@v5`
2. **Permissions**: Include appropriate `permissions` blocks
3. **Timeouts**: Set reasonable `timeout-minutes` (typically 30 minutes)
4. **Error Handling**: Include proper error handling and validation
5. **Documentation**: Clear workflow names and descriptions

## Target Architecture

- **Total Workflows**: ~12 quality workflows (reduced from 40+)
- **Core Build/Test**: 3-4 workflows
- **PR Validation**: 2-3 workflows  
- **Release/Deployment**: 2-3 workflows
- **Maintenance**: 2-3 workflows
- **Security Scanning**: 1-2 workflows

## Benefits

✅ **Faster CI execution** - Less queue time with fewer workflows
✅ **Clearer purpose** - Each workflow has a specific, well-defined role
✅ **Reduced maintenance** - Fewer workflows to maintain and debug
✅ **Better organization** - Logical grouping by function
✅ **Modern practices** - Updated to use latest GitHub Actions

## Migration Notes

This structure was created as part of the strategic CI/CD modernization effort to:
- Remove inherited upstream workflows not needed in the fork
- Consolidate duplicate functionality
- Modernize action versions and configurations
- Establish clear workflow ownership and purpose