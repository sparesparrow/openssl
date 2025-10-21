# ADR-002: Minimal Conan Integration Strategy

## Status

✅ Accepted

## Context

OpenSSL needed modern package management capabilities while maintaining compatibility with the upstream repository. The challenge was balancing modern development needs with the conservative approach of the upstream OpenSSL project.

## Decision

Implement **minimal, upstream-friendly** Conan integration that:

1. **Preserves traditional build system** (Configure/Make)
2. **Adds minimal package definition** (`conanfile.py`)
3. **Supports core configurations** (shared/static, FIPS/non-FIPS)
4. **Maintains 100% API compatibility**
5. **Enables modern CI/CD** without breaking changes

### Integration Scope

**Included in Main Repository**:
- `conanfile.py` with basic package definition
- `test_package/` for validation
- Minimal CI/CD workflows for triggering
- Basic profiles for common configurations

**Excluded from Main Repository**:
- Complex build tooling (moved to `openssl-tools`)
- Advanced CI/CD orchestration
- Package distribution and signing
- Cross-platform build matrices
- Security scanning and compliance

### Configuration Surface

**Exposed Options** (Minimal):
- `shared`: True/False (library linking type)
- `fPIC`: True/False (position-independent code)
- `enable_fips`: True/False (FIPS mode)
- `enable_tests`: True/False (unit tests)
- `enable_docs`: True/False (documentation)
- `no_deprecated`: True/False (exclude deprecated algorithms)

**Hidden Complexity**:
- Advanced compiler flags
- Platform-specific optimizations
- Build system selection (CMake vs Configure)
- Cross-compilation settings
- Cache optimization strategies

## Rationale

### Alternatives Considered

1. **Comprehensive Integration**: Full Conan integration in main repository
   - ❌ **Upstream resistance**: Too many changes for conservative project
   - ❌ **Maintenance burden**: Complex build system changes
   - ❌ **Risk**: Potential breaking changes to traditional builds

2. **No Integration**: Traditional builds only
   - ❌ **Modern development**: No support for package management
   - ❌ **CI/CD limitations**: Difficult automation and distribution
   - ❌ **Developer experience**: Manual dependency management

3. **External Integration**: Separate package repository
   - ❌ **Maintenance complexity**: Multiple repositories to maintain
   - ❌ **Version drift**: Risk of source and package divergence
   - ❌ **Trust issues**: External packages may not match source

### Trade-offs Evaluated

**Minimal Approach Benefits**:
- ✅ **Upstream compatibility**: Easy to merge upstream changes
- ✅ **Zero breaking changes**: Traditional builds unchanged
- ✅ **Conservative approach**: Matches OpenSSL project philosophy
- ✅ **Focused scope**: Clear separation of concerns
- ✅ **Maintainability**: Simple integration, easy to understand

**Minimal Approach Drawbacks**:
- ❌ **Limited flexibility**: Fewer configuration options
- ❌ **Advanced features**: Complex builds require tools repository
- ❌ **Learning curve**: Two-step process for advanced usage
- ❌ **Documentation complexity**: Need to explain architecture

### Constraints Addressed

1. **Upstream Compatibility**: Minimal changes ensure merge compatibility
2. **Conservative Project**: Respects OpenSSL's approach to changes
3. **Modern Requirements**: Provides package management without complexity
4. **Team Resources**: Allows specialization (crypto vs tooling teams)

## Consequences

### Positive Consequences

- **Easy Maintenance**: Simple integration reduces maintenance burden
- **Upstream Merging**: Minimal conflicts during upstream synchronization
- **Traditional Compatibility**: Zero impact on existing workflows
- **Clear Architecture**: Obvious separation between core and tooling
- **Gradual Adoption**: Teams can adopt modern tooling incrementally

### Negative Consequences

- **Two-Step Process**: Advanced usage requires understanding two repositories
- **Limited Configuration**: May not meet all specialized build requirements
- **Documentation Overhead**: Need comprehensive documentation for architecture
- **Coordination Required**: Changes may need coordination between repositories

### Additional Work Required

1. **Cross-repository Workflows**: Implement CI/CD that coordinates between repos
2. **Version Compatibility**: Ensure repositories work together
3. **Documentation**: Create comprehensive usage and migration guides
4. **Testing Strategy**: Validate both traditional and Conan builds
5. **Team Processes**: Define processes for maintaining both repositories

### Milestones Affected

- **Phase 1**: Minimal integration in main repository (Complete)
- **Phase 2**: Tools repository with advanced features (In Progress)
- **Phase 3**: Full ecosystem integration (Planned)

## References

- [Conan Improvements Summary](CONAN-IMPROVEMENTS-SUMMARY.md)
- [Building with Conan](BUILDING-CONAN.md)
- [Upstream OpenSSL Build Instructions](INSTALL.md)
- [Two-Repository Architecture](architecture/001-two-repository-pattern.md)

## Date

2024-10-17
