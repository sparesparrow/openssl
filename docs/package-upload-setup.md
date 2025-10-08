# Package Upload Setup Guide

This document explains how to configure package artifact uploads to multiple registries (Artifactory, GitHub Packages, Conan Center) for the OpenSSL project.

## Overview

The OpenSSL project now supports automatic package uploads to multiple registries:

- **Artifactory**: Primary package registry for OpenSSL packages
- **GitHub Packages**: GitHub's package registry
- **Conan Center**: Public package registry (optional)

## Configuration

### 1. Required Secrets

Configure the following secrets in your GitHub repository:

#### Artifactory Secrets
- `ARTIFACTORY_URL`: Base URL of your Artifactory instance
  - Example: `https://your-company.jfrog.io`
- `ARTIFACTORY_USERNAME`: Username for Artifactory authentication
- `ARTIFACTORY_PASSWORD`: Password or API key for Artifactory authentication

#### GitHub Packages (Automatic)
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- `GITHUB_ACTOR`: Automatically provided by GitHub Actions
- `GITHUB_REPOSITORY`: Automatically provided by GitHub Actions

#### Conan Center (Optional)
- `CONAN_CENTER_USERNAME`: Username for Conan Center
- `CONAN_CENTER_PASSWORD`: Password for Conan Center

### 2. How to Configure Secrets

1. Go to your GitHub repository
2. Click on "Settings" tab
3. Click on "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add each secret with the appropriate value

## Workflows

### 1. Package Artifacts Upload Workflow

The main workflow for package uploads is `.github/workflows/package-artifacts-upload.yml`:

- **Triggers**: Push to main/release branches, manual dispatch
- **Features**: 
  - Multi-platform builds (Linux, Windows, macOS)
  - Upload to multiple registries
  - Automatic GitHub releases
  - Artifact retention

### 2. Updated Conan CI Workflow

The existing `.github/workflows/conan-ci.yml` has been updated to include:

- Package upload to Artifactory (if configured)
- Package upload to GitHub Packages (on main branch)
- Enhanced artifact uploads with retention

## Usage

### Manual Upload

To manually upload packages:

```bash
# Using the package registry manager
python scripts/conan/package-registry-manager.py \
  --package-ref "openssl/4.0.0@openssl/stable" \
  --registries artifactory github-packages
```

### Automatic Upload

Packages are automatically uploaded when:

1. Pushing to main branch (uploads to GitHub Packages)
2. Pushing to release branches (uploads to all configured registries)
3. Manual workflow dispatch

## Installation Instructions

### From Artifactory

```bash
# Add Artifactory remote
conan remote add artifactory https://your-artifactory.com/conan-local

# Authenticate
conan user -p <password> -r artifactory <username>

# Install OpenSSL package
conan install openssl/4.0.0@openssl/stable -r=artifactory
```

### From GitHub Packages

```bash
# Add GitHub Packages remote
conan remote add github-packages https://maven.pkg.github.com/openssl/openssl

# Authenticate
conan user -p <github_token> -r github-packages <username>

# Install OpenSSL package
conan install openssl/4.0.0@openssl/stable -r=github-packages
```

### From Conan Center

```bash
# Install OpenSSL package (no additional setup needed)
conan install openssl/4.0.0@openssl/stable
```

## Monitoring

### Upload Status

Check the workflow runs in the "Actions" tab to monitor upload status:

- Green checkmark: Upload successful
- Red X: Upload failed
- Yellow circle: Upload in progress

### Package Availability

Verify packages are available in registries:

```bash
# List packages in Artifactory
conan list "*" -r artifactory

# List packages in GitHub Packages
conan list "*" -r github-packages

# List packages in Conan Center
conan list "*" -r conancenter
```

## Troubleshooting

### Common Issues

1. **Upload fails with authentication error**
   - Check that secrets are properly configured
   - Verify credentials are correct
   - Ensure the user has upload permissions

2. **Package not found after upload**
   - Wait a few minutes for registry synchronization
   - Check the correct registry is being used
   - Verify the package reference is correct

3. **Workflow fails to trigger**
   - Check that the workflow file is in `.github/workflows/`
   - Verify the trigger conditions are met
   - Check for syntax errors in the workflow file

### Debug Commands

```bash
# Test package upload functionality
python scripts/test-package-upload.py

# Check Conan configuration
conan config list

# List configured remotes
conan remote list

# Test registry connectivity
conan search "*" -r <registry-name>
```

## Security Considerations

1. **Secrets Management**
   - Never commit secrets to the repository
   - Use GitHub Secrets for sensitive information
   - Rotate credentials regularly

2. **Package Signing**
   - Consider enabling package signing for production
   - Verify package integrity before installation
   - Use checksums for package validation

3. **Access Control**
   - Limit upload permissions to trusted users
   - Use separate credentials for different environments
   - Monitor upload activities

## Best Practices

1. **Version Management**
   - Use semantic versioning for packages
   - Tag releases appropriately
   - Maintain backward compatibility

2. **Registry Management**
   - Use multiple registries for redundancy
   - Implement proper retention policies
   - Monitor registry health

3. **Documentation**
   - Keep installation instructions up to date
   - Document any breaking changes
   - Provide migration guides

## Support

For issues related to package uploads:

1. Check the workflow logs in GitHub Actions
2. Review the troubleshooting section above
3. Open an issue in the repository
4. Contact the maintainers

## Files Modified

The following files have been created or modified for package upload functionality:

### New Files
- `.github/workflows/package-artifacts-upload.yml` - Main upload workflow
- `scripts/conan/package-registry-manager.py` - Registry management script
- `scripts/test-package-upload.py` - Upload testing script
- `scripts/update-workflows-package-upload.py` - Workflow updater
- `conan-dev/package-registries.yml` - Registry configuration
- `docs/package-upload-setup.md` - This documentation

### Modified Files
- `.github/workflows/conan-ci.yml` - Added upload steps
- Various workflow files - Updated with upload functionality

## Conclusion

The package upload system provides a robust, multi-registry solution for distributing OpenSSL packages. With proper configuration and monitoring, it ensures reliable package availability across different platforms and use cases.