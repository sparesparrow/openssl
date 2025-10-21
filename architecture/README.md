# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records documenting the key architectural decisions made in this OpenSSL fork.

## What are ADRs?

Architecture Decision Records are documents that capture important architectural decisions along with their context and consequences. They help:

- **Communicate decisions** to current and future team members
- **Document rationale** for why decisions were made
- **Provide context** for understanding the system architecture
- **Support onboarding** of new team members

## Template

Each ADR should follow this template:

```markdown
# ADR-XXX: Title

## Status

- [ ] Proposed
- [ ] Accepted
- [ ] Rejected
- [x] Deprecated
- [ ] Superseded by [ADR-XXX]

## Context

Describe the context and problem being solved.

## Decision

Describe the decision that was made.

## Rationale

Explain why this decision was made, including:
- Alternatives considered
- Trade-offs evaluated
- Constraints addressed

## Consequences

Describe the resulting context and follow-up decisions:
- Positive consequences
- Negative consequences
- Additional work required
- Milestones or deadlines affected

## References

- Links to related discussions, issues, or PRs
- External documentation or standards
- Related ADRs

## Date

YYYY-MM-DD when the decision was made.
```

## Index of ADRs

| ADR | Title | Status | Date |
|-----|--------|--------|------|
| [001](001-two-repository-pattern.md) | Two-Repository Architecture | Accepted | 2024-10-17 |
| [002](002-minimal-conan-integration.md) | Minimal Conan Integration Strategy | Accepted | 2024-10-17 |
| [003](003-security-workflow-selection.md) | Security Workflow and Tool Selection | Accepted | 2024-10-17 |
| [004](004-version-management-strategy.md) | Version Management Between Repositories | Accepted | 2024-10-17 |
| [005](005-ci-cd-optimization-strategy.md) | CI/CD Optimization and Caching Strategy | Accepted | 2024-10-17 |
