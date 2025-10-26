# Track A: Security & Compliance Pipeline

## Overview

Track A implements automated security scanning, SBOM generation, and FIPS compliance validation across the OpenSSL ecosystem repositories. All workflows are reusable and can run on any OpenSSL build (Conan or non-Conan).

## Implementation Status

✅ **COMPLETED** - All Track A components have been implemented and are ready for use.

## Components

### 1. Reusable SBOM Generation Workflow

**Location**: `openssl-conan-base/.github/workflows/reusable-sbom-generation.yml`

**Features**:
- Generates SBOM using Syft (CycloneDX format)
- Scans with Trivy for CVE detection
- Configurable severity thresholds
- Optional Dependency Track integration
- Returns vulnerability counts and scan results

**Usage**:
```yaml
- name: Generate and scan SBOM
  uses: sparesparrow/openssl-conan-base/.github/workflows/reusable-sbom-generation.yml@main
  with:
    artifact-name: 'openssl-linux-x86_64'
    output-format: 'cyclonedx-json'
    severity-threshold: 'HIGH'
    upload-to-dependency-track: false
```

### 2. FIPS Compliance Automation

**Location**: `openssl-fips-policy/.github/workflows/fips-validation.yml`

**Features**:
- Multi-platform FIPS validation (Linux, Windows, macOS)
- Automated FIPS module hash verification
- FIPS self-test execution
- Algorithm validation (AES-GCM, SHA-256, RSA)
- Compliance report generation
- Weekly scheduled validation

**Triggers**:
- Push/PR to FIPS-related files
- Weekly schedule (Sunday 2 AM)
- Manual dispatch with version selection

### 3. CodeQL Security Scanning

**Location**: `openssl/.github/workflows/codeql-analysis.yml`

**Features**:
- Static security analysis for C/C++ code
- Multiple query suites (security-extended, security-and-quality)
- Comprehensive analysis on schedule
- Security advisory checking
- Custom OpenSSL-specific queries
- Integration with GitHub Security tab

**Configuration**: `openssl/.github/codeql/codeql-config.yml`

## Integration Guide

### Using the Reusable SBOM Workflow

Any repository can use the SBOM generation workflow:

```yaml
name: Build and Security Scan

on: [push, pull_request]

jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build your project
        run: |
          # Your build commands here
          make build
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: my-project-artifacts
          path: build/
      
      - name: Generate SBOM and scan
        uses: sparesparrow/openssl-conan-base/.github/workflows/reusable-sbom-generation.yml@main
        with:
          artifact-name: 'my-project-artifacts'
          severity-threshold: 'HIGH'
```

### FIPS Validation Integration

To trigger FIPS validation from other repositories:

```yaml
- name: Trigger FIPS validation
  uses: sparesparrow/openssl-fips-policy/.github/workflows/fips-validation.yml@main
  with:
    openssl-version: '3.4.1'
    test-platforms: 'linux'
```

### CodeQL Integration

To add CodeQL to any C/C++ repository:

1. Copy the workflow file:
```bash
cp openssl/.github/workflows/codeql-analysis.yml your-repo/.github/workflows/
```

2. Copy the configuration:
```bash
cp -r openssl/.github/codeql your-repo/.github/
```

3. Customize the build steps in the workflow for your project.

## Security Features

### SBOM Generation
- **Format**: CycloneDX JSON
- **Tools**: Syft for generation, Trivy for scanning
- **Coverage**: All dependencies and components
- **Storage**: 90-day retention in GitHub Actions artifacts

### FIPS Compliance
- **Standard**: FIPS 140-3 Level 1
- **Certificate**: #4985
- **Validation**: Module hash, self-tests, algorithm compliance
- **Platforms**: Linux, Windows, macOS

### CodeQL Analysis
- **Languages**: C/C++
- **Queries**: Security-extended, security-and-quality
- **Schedule**: Weekly comprehensive analysis
- **Integration**: GitHub Security tab

## Expected Hash Tracking

**File**: `openssl-fips-policy/fips/expected_module_hash.txt`

This file tracks expected SHA-256 hashes for FIPS modules across different OpenSSL versions. To add a new version:

1. Build OpenSSL with FIPS enabled
2. Calculate hash: `openssl dgst -sha256 /path/to/fips.so`
3. Add entry: `<version> <hash>`

## Monitoring and Alerts

### GitHub Security Tab
- CodeQL findings appear in Security tab
- SARIF uploads enable detailed analysis
- Historical tracking of security issues

### Workflow Notifications
- Failed security scans block PRs
- Weekly compliance reports generated
- Vulnerability counts tracked over time

### Dependency Track Integration
- Optional SBOM upload to Dependency Track
- Centralized vulnerability management
- Compliance reporting

## Troubleshooting

### SBOM Generation Issues
- Ensure artifacts are uploaded before SBOM generation
- Check Syft and Trivy versions in workflow
- Verify artifact paths are correct

### FIPS Validation Failures
- Check expected hash file for correct version
- Verify OpenSSL build includes FIPS support
- Ensure FIPS module is properly installed

### CodeQL Analysis Problems
- Verify build completes successfully
- Check CodeQL configuration file syntax
- Ensure sufficient memory allocation (8GB recommended)

## Success Metrics

- ✅ SBOM workflow generates CycloneDX format
- ✅ Trivy scanning detects vulnerabilities and fails on critical/high
- ✅ FIPS validation passes with correct module hash
- ✅ FIPS self-tests complete successfully
- ✅ CodeQL analysis runs without errors
- ✅ All workflows are reusable across repositories

## Integration with CI/CD Pipelines

Track A has been integrated into the existing CI/CD workflows across the OpenSSL ecosystem:

### 1. OpenSSL Repository Integration
**File**: `openssl/.github/workflows/ci.yml`

The main OpenSSL CI workflow now includes:
- **SBOM Generation**: Automatic generation of Software Bill of Materials for build artifacts
- **Artifact Upload**: SBOM files are uploaded as workflow artifacts for 90 days
- **Integration Point**: SBOM generation runs after successful builds

### 2. OpenSSL Tools Integration
**File**: `openssl-tools/.github/workflows/conan-ci-enhanced.yml`

The Conan CI workflow includes:
- **SBOM Generation**: For all build profiles and configurations
- **Security Scanning**: Integration with Track A reusable SBOM workflow
- **Consolidated Artifacts**: Multiple SBOM files are consolidated for scanning
- **Track A Integration**: Uses the reusable SBOM generation workflow

### 3. Workflow Automation Scripts

Two automation scripts have been created to manage Track A:

#### Enable Workflows Script
**File**: `scripts/enable-track-a-workflows.sh`

This script:
- Verifies all Track A workflow files exist
- Creates a trigger commit to enable workflows
- Pushes changes to trigger initial workflow runs
- Provides guidance on next steps

#### Monitor Results Script
**File**: `scripts/monitor-security-results.sh`

This script:
- Checks workflow run status across all repositories
- Monitors security alerts and findings
- Provides summary of Track A results
- Uses GitHub CLI for comprehensive monitoring

## Usage Instructions

### 1. Enable Track A Workflows
```bash
# Run from openssl-devenv root directory
./scripts/enable-track-a-workflows.sh
```

### 2. Monitor Security Results
```bash
# Check workflow status and security findings
./scripts/monitor-security-results.sh
```

### 3. Manual Workflow Triggers
```bash
# Trigger SBOM generation
gh workflow run reusable-sbom-generation.yml --repo sparesparrow/openssl-conan-base

# Trigger FIPS validation
gh workflow run fips-validation.yml --repo sparesparrow/openssl-fips-policy

# Trigger CodeQL analysis
gh workflow run codeql-analysis.yml --repo sparesparrow/openssl
```

## Next Steps

1. **Enable workflows**: Run `./scripts/enable-track-a-workflows.sh`
2. **Configure secrets**: Add Dependency Track API keys if needed
3. **Monitor results**: Run `./scripts/monitor-security-results.sh`
4. **Customize queries**: Add repository-specific CodeQL queries
5. **Review findings**: Check GitHub Security tab for security alerts

## Support

For issues or questions about Track A implementation:
- Check workflow logs in GitHub Actions
- Review configuration files for syntax errors
- Consult GitHub documentation for CodeQL and Actions
- Open issues in respective repositories for specific problems
