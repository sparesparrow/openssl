# OpenSSL Development Environment

**Orchestration Hub for DDD 4-Repository Layered Architecture Testing**

This workspace provides a complete development and testing environment for the OpenSSL layered architecture ecosystem. It contains 8 repositories organized across 4 architectural layers, enabling comprehensive testing of dependency management, CI/CD pipelines, AI integration, and cross-repository workflows.

## 🏗️ Architecture Overview

```mermaid
graph TB
    subgraph "Foundation Layer"
        BASE[openssl-conan-base<br/>📦 Utilities + Profiles]
        POLICY[openssl-fips-policy<br/>📦 FIPS Certificates]
    end
    
    subgraph "Tooling Layer"
        TOOLS[openssl-tools<br/>📦 Build Orchestration]
    end
    
    subgraph "Domain Layer"
        OPENSSL[openssl<br/>📦 Cryptographic Library]
    end
    
    subgraph "Orchestration Layer"
        MCP[mcp-project-orchestrator<br/>🤖 AI Templates]
    end
    
    subgraph "Testing & Integration"
        FUZZ[fuzz-corpora<br/>🔬 Test Data]
        DOCS[openssl-docs<br/>📚 Documentation]
        CURL[libcurl<br/>🌐 HTTP Integration]
    end
    
    subgraph "Distribution"
        CLOUDSMITH[(Cloudsmith<br/>${CONAN_REPOSITORY_NAME})]
    end
    
    BASE --> CLOUDSMITH
    POLICY --> CLOUDSMITH
    TOOLS --> CLOUDSMITH
    OPENSSL --> CLOUDSMITH
    
    TOOLS -.->|requires| BASE
    TOOLS -.->|requires| POLICY
    OPENSSL -.->|tool_requires| TOOLS
    
    MCP -.->|creates| PROJECTS[Test Projects]
    PROJECTS -.->|depends on| OPENSSL
    
    FUZZ -.->|tests| OPENSSL
    DOCS -.->|documents| OPENSSL
    CURL -.->|integrates| OPENSSL
```

## 📁 Repository Structure

### 🔐 Foundation Layer
**openssl-conan-base** - Foundation utilities for OpenSSL Conan ecosystem
- **Purpose**: Version management, SBOM generation, profile deployment
- **Key Components**: `openssl_base/` package with utilities and tests
- **CI/CD**: Publishes `openssl-base/1.0.0` to Cloudsmith

**openssl-fips-policy** - FIPS 140-3 compliance artifacts
- **Purpose**: FIPS certificates and validation data
- **Key Components**: Certificate #4985 data and schemas
- **CI/CD**: Publishes `openssl-fips-data/140-3.1` to Cloudsmith

### 🛠️ Tooling Layer
**openssl-tools** - Build orchestration consuming foundation packages
- **Purpose**: Bridge between foundation and domain layers
- **Dependencies**: `openssl-base/1.0.0`, `openssl-fips-data/140-3.1`
- **CI/CD**: Publishes `openssl-build-tools/1.2.0` to Cloudsmith

### 🔬 Testing & Integration Layer
**fuzz-corpora** - Fuzz testing data and corpora
- **Purpose**: Test data for OpenSSL fuzzing and validation

**openssl-docs** - Documentation and guides
- **Purpose**: Comprehensive OpenSSL documentation

**libcurl** - HTTP library for integration testing
- **Purpose**: Test OpenSSL integration with HTTP clients

### 🌐 Domain Layer
**openssl** - OpenSSL cryptographic library with layered architecture
- **Purpose**: Core cryptographic functionality with Conan packaging
- **Features**: 5-phase build, deployment targets, FIPS integration
- **Dependencies**: `openssl-build-tools/1.2.0`
- **CI/CD**: Publishes `openssl/3.4.1` to Cloudsmith

### 🤖 Orchestration Layer
**mcp-project-orchestrator** - AI-enhanced project creation
- **Purpose**: Templates, Cursor integration, MCP server
- **Features**: OpenSSL project templates, AI development assistance

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone and open workspace
cd ~/projects/openssl-devenv
code openssl-devenv.code-workspace

# Or use devcontainer
# Open in VSCode/Cursor with devcontainer support
```

### 2. Initial Configuration
```bash
# Set Cloudsmith API key
export CLOUDSMITH_API_KEY="your-api-key-here"

# Run setup script
./scripts/setup-dev-env.sh
```

### 3. Basic Testing
```bash
# Test foundation layer
cd openssl-conan-base && conan create . --build=missing

# Test tooling layer  
cd ../openssl-tools && conan create . --build=missing

# Test domain layer
cd ../openssl && conan create . --build=missing
```

## 🧪 Testing Scenarios & Procedures

### 1. Dependency Management Testing
**Objective**: Verify package dependencies resolve correctly across layers

**Procedure**:
```bash
cd openssl-tools
conan create . --build=missing
```

**Expected Results**:
- ✅ Downloads `openssl-base/1.0.0` and `openssl-fips-data/140-3.1` from Cloudsmith
- ✅ No local builds required for foundation packages
- ✅ Package published as `openssl-build-tools/1.2.0`

**Success Criteria**:
- Build completes without errors
- All transitive dependencies resolved
- Package appears in local cache

### 2. Python Automation Testing
**Objective**: Test foundation utilities and orchestration scripts

**Procedure**:
```bash
cd openssl-conan-base
python -c "from openssl_base import get_openssl_version, generate_openssl_sbom; print('FIPS version:', get_openssl_version('3.4.1', True))"
pytest tests/ -v
```

**Expected Results**:
- ✅ Version manager generates hybrid semantic+FIPS versions
- ✅ SBOM generator creates valid CycloneDX format
- ✅ Profile deployer works correctly
- ✅ All unit tests pass

### 3. Cloudsmith Integration Testing
**Objective**: Verify package publishing and remote consumption

**Procedure**:
```bash
# Check published packages
conan search "*" -r=${CONAN_REPOSITORY_NAME}

# Test remote installation
conan install --requires=openssl-build-tools/1.2.0 -r=${CONAN_REPOSITORY_NAME}
```

**Expected Results**:
- ✅ All 4 packages visible in remote
- ✅ Remote installation succeeds
- ✅ No authentication errors

### 4. Conan Environment Testing
**Objective**: Test virtual environments and dependency isolation

**Procedure**:
```bash
cd mcp-project-orchestrator
python -m venv venv
source venv/bin/activate
pip install -e .
mcp-orchestrator create-openssl-project --project-name venv-test
```

**Expected Results**:
- ✅ Virtual environment isolates dependencies
- ✅ MCP orchestrator installs correctly
- ✅ Project creation generates proper structure

### 5. Remote Artifact Caching
**Objective**: Test Conan caching behavior

**Procedure**:
```bash
# First run (downloads)
time conan create openssl-conan-base --build=missing

# Second run (cached)
time conan create openssl-conan-base --build=missing
```

**Expected Results**:
- ✅ First run downloads dependencies
- ✅ Second run uses cached artifacts
- ✅ Significant performance improvement

### 6. Developer Workflow Simulation
**Objective**: Test complete development workflow

**Procedure**:
```bash
cd mcp-project-orchestrator
source venv/bin/activate
mcp-orchestrator create-openssl-project --project-name workflow-test --deployment-target fips-government

cd ../workflow-test
conan install . --build=missing
cmake --preset conan-default
cmake --build --preset conan-release
./build/Release/workflow-test
```

**Expected Results**:
- ✅ Project creates with FIPS options
- ✅ Dependencies resolve correctly
- ✅ Build completes successfully
- ✅ Application runs with FIPS indicators

### 7. Domain Repository Compile Performance
**Objective**: Measure build performance

**Procedure**:
```bash
cd openssl
time conan create . --build=missing -o deployment_target=general
time conan create . --build=missing -o deployment_target=fips-government
```

**Expected Results**:
- ✅ General build: 5-10 minutes
- ✅ FIPS build: Additional validation time
- ✅ Performance metrics collected

### 8. Integration Testing
**Objective**: Test cross-repository interactions

**Procedure**:
```bash
# Build dependency chain
cd openssl-conan-base && conan create . --build=missing
cd ../openssl-fips-policy && conan create . --build=missing
cd ../openssl-tools && conan create . --build=missing
cd ../openssl && conan create . --build=missing

# Test template system
cd ../mcp-project-orchestrator
source venv/bin/activate
mcp-orchestrator create-openssl-project --project-name integration-test
```

**Expected Results**:
- ✅ All repositories build successfully
- ✅ Dependencies resolve across layers
- ✅ Template system generates functional projects

### 9. AI Integration Testing
**Objective**: Test Cursor and MCP functionality

**Procedure**:
```bash
cd mcp-project-orchestrator
source venv/bin/activate
mcp-orchestrator deploy-cursor --project-type openssl

# Start MCP server
python -m mcp_project_orchestrator
```

**Expected Results**:
- ✅ Cursor configuration deploys
- ✅ MCP server starts on port 8080
- ✅ AI recognizes OpenSSL patterns

### 10. GitHub Actions & Workflow Testing
**Objective**: Test CI/CD pipeline triggers

**Procedure**:
```bash
cd openssl-conan-base
echo "# Test CI trigger" >> README.md
git add README.md
git commit -m "test: trigger CI pipeline"
git push origin main
```

**Expected Results**:
- ✅ GitHub Actions workflow triggers
- ✅ Build and publish steps execute
- ✅ Package appears in Cloudsmith

## 🔧 Component Behavior Expectations

### Foundation Layer Behavior

**openssl-conan-base Components**:
- **Version Manager**: Generates semantic versions for general builds, hybrid versions for FIPS
- **SBOM Generator**: Creates CycloneDX format with compliance metadata
- **Profile Deployer**: Installs Conan profiles to `~/.conan2/profiles/`
- **Expected**: Self-contained, no external dependencies, comprehensive test coverage

**openssl-fips-policy Components**:
- **Certificate Data**: Exports FIPS 140-3 certificate #4985
- **Validation Rules**: Provides compliance checking utilities
- **Expected**: Static data package, integrity verification, government deployment ready

### Tooling Layer Behavior

**openssl-tools Components**:
- **Build Orchestration**: Coordinates foundation package usage
- **Environment Setup**: Exposes `OPENSSL_BUILD_TOOLS_VERSION`
- **Dependency Resolution**: Pulls from Cloudsmith, never builds foundation locally
- **Expected**: Fast builds, comprehensive dependency management, CI/CD integration

### Domain Layer Behavior

**openssl Components**:
- **5-Phase Build**: Source prep → Configure → Build → Test → FIPS validation
- **Deployment Targets**: General (standard), FIPS-government (validated), Embedded (optimized)
- **FIPS Integration**: Certificate #4985, security checks, compliance metadata
- **SBOM Generation**: CycloneDX with deployment target metadata
- **Expected**: Aerospace-quality process, comprehensive validation, multi-platform support

### Orchestration Layer Behavior

**mcp-project-orchestrator Components**:
- **Template Engine**: Jinja2 rendering for project creation
- **Cursor Deployment**: IDE configuration for OpenSSL development
- **MCP Server**: AI assistance and project orchestration
- **Expected**: Rapid prototyping, AI-enhanced development, multi-repository coordination

## 🚨 Troubleshooting Guide

### Conan Remote Issues
```bash
# Verify remote
conan remote list

# Re-authenticate
conan remote login ${CONAN_REPOSITORY_NAME} spare-sparrow --password "$CLOUDSMITH_API_KEY"

# Clear problematic cache
conan cache clean
rm -rf ~/.conan2/p/*
```

### Build Failures
```bash
# Check dependency info
conan info .

# Verify environment
python --version && conan --version

# Clean rebuild
conan cache clean
conan create . --build=missing
```

### Template System Issues
```bash
cd mcp-project-orchestrator
source venv/bin/activate
python -c "
from mcp_project_orchestrator.templates import TemplateManager
tm = TemplateManager('templates')
tm.discover_templates()
print('Found templates:', tm.list_templates())
"
```

### FIPS Validation Issues
```bash
# Check certificate data
cd openssl-fips-policy
python -c "
import json
with open('fips-140-3/certificates/certificate-4985.json') as f:
    cert = json.load(f)
print('Certificate expires:', cert['expiry_date'])
"
```

### Performance Issues
```bash
# Check build times
time conan create . --build=missing

# Profile build
conan build . --profile=linux-gcc-release
```

## 📊 Performance Benchmarks

### Expected Build Times
- **openssl-conan-base**: < 30 seconds (Python utilities)
- **openssl-fips-policy**: < 10 seconds (data package)
- **openssl-tools**: < 60 seconds (dependency resolution)
- **openssl**: 5-15 minutes (full cryptographic library)

### Cache Effectiveness
- **First builds**: Download all dependencies
- **Cached builds**: < 20% of original time
- **Clean cache penalty**: 3-5x slower

## 🔒 Security Considerations

### FIPS Compliance Requirements
- Use only validated algorithms (AES-GCM, SHA-256, RSA-2048+)
- Enable FIPS mode for government deployments
- Include certificate metadata in SBOMs
- Verify FIPS module integrity

### Supply Chain Security
- All packages scanned for vulnerabilities
- SBOM generation enables dependency verification
- Signed releases with reproducible builds
- No hardcoded credentials in source code

### Development Environment Security
- Secrets managed via GitHub repository secrets
- Virtual environments isolate development dependencies
- SSH authentication for all git operations

## 🎯 Success Criteria Verification

### Repository Health
- [ ] All 8 repositories cloned successfully
- [ ] No merge conflicts or broken builds
- [ ] All CI/CD workflows functional

### Layer Integration
- [ ] Foundation packages published to Cloudsmith
- [ ] Tooling layer consumes foundation correctly
- [ ] Domain layer builds with 5-phase process
- [ ] Orchestration layer creates functional projects

### Cross-Repository Dependencies
- [ ] Package dependencies resolve correctly
- [ ] Remote artifact caching works
- [ ] No circular dependencies

### AI Integration
- [ ] Cursor configuration deploys correctly
- [ ] MCP server provides assistance
- [ ] Template system generates valid projects

### Performance & Reliability
- [ ] Build times within expected ranges
- [ ] Cache effectiveness demonstrated
- [ ] All integration tests pass

This environment serves as the complete testing ground for the OpenSSL layered architecture, enabling comprehensive validation of all components, workflows, and integrations.
