# ADR-001: Two-Repository Architecture

## Status

✅ Accepted

## Context

The OpenSSL project needed modernization to support:
- Modern package management (Conan 2.x)
- Enhanced CI/CD with security scanning
- Build optimization and caching
- Artifact distribution and deployment
- FIPS compliance validation
- Cross-platform compatibility testing

The traditional monolithic repository approach would require significant changes to the upstream OpenSSL build system and CI/CD processes, making upstream merging difficult and potentially introducing breaking changes.

## Decision

Implement a **two-repository architecture**:

1. **Main repository** (`sparesparrow/openssl`): Core OpenSSL source code with minimal Conan integration
2. **Tools repository** (`sparesparrow/openssl-tools`): Build tooling, CI/CD orchestration, and package distribution

### Repository Responsibilities

**Main Repository (`openssl`)**:
- Core OpenSSL cryptographic implementation (100% upstream compatible)
- Minimal Conan integration (`conanfile.py`, basic profiles)
- Traditional Configure/Make build system (preserved)
- Basic CI/CD for validation and triggering
- Test package for validation

**Tools Repository (`openssl-tools`)**:
- Advanced CI/CD orchestration
- Conan package building and distribution
- Build optimization and caching strategies
- Security scanning (CodeQL, Trivy, SBOM)
- Artifact signing and distribution
- Cross-repository dependency management

## Rationale

### Alternatives Considered

1. **Monolithic Repository**: Single repository with all tooling
   - ❌ **High risk**: Major changes to upstream build system
   - ❌ **Merge complexity**: Difficult upstream synchronization
   - ❌ **Breaking changes**: Risk of compatibility issues

2. **Upstream Contribution**: Contribute directly to openssl/openssl
   - ❌ **Acceptance uncertainty**: Conservative upstream approach
   - ❌ **Timeline risk**: Long review and acceptance process
   - ❌ **Feature limitations**: May not accept all modern tooling

3. **Fork-only Approach**: Single repository fork with all enhancements
   - ❌ **Maintenance burden**: All upstream merging in one repository
   - ❌ **Complexity**: Mixing core crypto and tooling concerns
   - ❌ **Team coordination**: All changes require crypto expertise

### Trade-offs Evaluated

**Positive Aspects**:
- ✅ **Separation of concerns**: Crypto implementation separate from tooling
- ✅ **Upstream compatibility**: Minimal changes to core repository
- ✅ **Independent evolution**: Tooling can evolve without crypto changes
- ✅ **Team specialization**: Different teams can focus on different areas
- ✅ **Reduced merge conflicts**: Fewer conflicts during upstream sync

**Negative Aspects**:
- ❌ **Cross-repository coordination**: Requires managing dependencies between repos
- ❌ **Version compatibility**: Need to ensure repo versions work together
- ❌ **Documentation complexity**: Need to explain two-repo relationship
- ❌ **CI/CD complexity**: Workflows need to coordinate across repositories

### Constraints Addressed

1. **Upstream Compatibility**: Minimal changes ensure easy merging
2. **Security Requirements**: FIPS compliance and security scanning
3. **Modern Development**: Support for Conan and modern CI/CD
4. **Team Resources**: Allow specialization in different areas

## Consequences

### Positive Consequences

- **Easy Upstream Merging**: Minimal changes reduce merge complexity
- **Modern Tooling**: Full support for Conan, security scanning, optimization
- **Team Focus**: Crypto team focuses on implementation, tools team on automation
- **Scalability**: Each repository can scale independently
- **Risk Mitigation**: Issues in tooling don't affect core crypto functionality

### Negative Consequences

- **Coordination Overhead**: Need to manage cross-repository dependencies
- **Version Management**: Must ensure compatibility between repositories
- **Documentation Burden**: Need comprehensive docs explaining architecture
- **CI/CD Complexity**: Multi-repository workflows require careful design

### Additional Work Required

1. **Cross-repository CI/CD**: Implement workflows that coordinate between repos
2. **Version Management**: Establish version compatibility validation
3. **Documentation**: Create comprehensive architecture documentation
4. **Team Processes**: Define processes for cross-repository collaboration
5. **Integration Testing**: Ensure repositories work together correctly

### Milestones Affected

- **Phase 1**: Core repository setup and minimal Conan integration (Complete)
- **Phase 2**: Tools repository and cross-repository coordination (In Progress)
- **Phase 3**: Full automation and optimization (Planned)

## References

- [Repository Separation Plan](REPOSITORY-SEPARATION-PLAN.md)
- [OpenSSL Tools Repository](https://github.com/sparesparrow/openssl-tools)
- [Conan Integration Discussion](#23)
- [Upstream OpenSSL Repository](https://github.com/openssl/openssl)

## Date

2024-10-17
