# ADR-004: Version Management Between Repositories

## Status

✅ Accepted

## Context

The two-repository architecture (openssl + openssl-tools) creates version compatibility challenges:
- Both repositories need compatible versions
- Package consumers need predictable version schemes
- CI/CD workflows need to coordinate between repositories
- Security updates need synchronized releases

## Decision

Implement **coordinated versioning** with:

### Version Scheme

**Main Repository (`openssl`)**:
- Primary version: Based on upstream OpenSSL (e.g., 4.0.0-dev)
- Conan package: `openssl/{version}@user/stable`
- Git tags: Follow upstream pattern (v4.0.0-dev)

**Tools Repository (`openssl-tools`)**:
- Independent versioning: Based on tooling maturity (e.g., 1.2.0)
- Conan extensions: `openssl-tools/{version}@user/stable`
- Git tags: Semantic versioning (v1.2.0)

### Compatibility Matrix

| OpenSSL Version | Tools Version | Compatibility | Support Level |
|----------------|---------------|---------------|---------------|
| 4.0.0-dev | 1.2.x | ✅ Full | Primary |
| 3.4.x | 1.1.x | ✅ Compatible | Maintenance |
| 3.3.x | 1.0.x | ⚠️ Legacy | Best Effort |

### Version Detection

**Dynamic Version Reading**:
- `conanfile.py` reads from `VERSION.dat`
- CI/CD workflows detect version automatically
- Package metadata includes build information

**Cross-Repository Validation**:
- CI checks compatibility matrix
- Automated testing validates repository pairs
- Version mismatch detection in workflows

## Rationale

### Alternatives Considered

1. **Synchronized Versioning**: Both repos use same version number
   - ❌ **Confusion**: Unclear which repo has which version
   - ❌ **Coupling**: Too tight coupling between repositories
   - ❌ **Maintenance**: Difficult to version independently

2. **Independent Versioning**: No coordination between repos
   - ❌ **Compatibility issues**: Risk of incompatible versions
   - ❌ **Support complexity**: Difficult to troubleshoot issues
   - ❌ **User confusion**: Unclear which versions work together

3. **Tools as Submodule**: Tools repo as submodule of main
   - ❌ **Maintenance burden**: Submodule management complexity
   - ❌ **CI/CD issues**: Submodule update complications
   - ❌ **Versioning**: Submodule pins specific commit, not version

### Trade-offs Evaluated

**Coordinated Approach Benefits**:
- ✅ **Clear compatibility**: Users know which versions work together
- ✅ **Independent evolution**: Each repo can evolve independently
- ✅ **Support clarity**: Clear support lifecycle for version pairs
- ✅ **Migration path**: Clear upgrade and migration guidance

**Coordinated Approach Drawbacks**:
- ❌ **Coordination overhead**: Need to manage compatibility matrix
- ❌ **Release complexity**: Coordinated releases between repos
- ❌ **Documentation burden**: Need to document compatibility
- ❌ **CI/CD complexity**: Need validation across repositories

### Constraints Addressed

1. **User Experience**: Clear guidance on compatible versions
2. **Support Complexity**: Manageable support matrix
3. **Evolution Speed**: Allow independent development pace
4. **Compatibility**: Ensure repositories work together

## Consequences

### Positive Consequences

- **User Clarity**: Clear guidance on version compatibility
- **Independent Development**: Each repository evolves at own pace
- **Support Manageability**: Clear support lifecycle
- **Migration Guidance**: Clear upgrade paths for users
- **Issue Resolution**: Easier troubleshooting with version pairs

### Negative Consequences

- **Release Coordination**: Need to coordinate releases between repos
- **Compatibility Testing**: Additional testing for version pairs
- **Documentation Overhead**: Need comprehensive compatibility docs
- **User Choice Complexity**: Users must understand compatibility matrix

### Additional Work Required

1. **Compatibility Validation**: Implement automated compatibility checking
2. **Release Coordination**: Define processes for coordinated releases
3. **Documentation**: Create comprehensive compatibility guides
4. **Migration Tools**: Tools to help users migrate between versions
5. **CI/CD Integration**: Workflows that validate cross-repository compatibility

### Milestones Affected

- **Phase 1**: Basic version coordination (Complete)
- **Phase 2**: Automated compatibility validation (In Progress)
- **Phase 3**: Advanced version management tools (Planned)

## References

- [Version Management Discussion](#23)
- [Repository Separation Plan](REPOSITORY-SEPARATION-PLAN.md)
- [Conan Package Versioning](https://docs.conan.io/2/reference/tools/scm/git.html)
- [Semantic Versioning](https://semver.org/)

## Date

2024-10-17
