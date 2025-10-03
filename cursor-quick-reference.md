# Cursor Quick Reference

## Essential Cursor Commands

### Code Generation
- `@generate` - Generate code from comments
- `@refactor` - Refactor existing code
- `@optimize` - Optimize code performance
- `@test` - Generate test cases
- `@document` - Generate documentation

### Conan-Specific Commands
- `@conan-create` - Create conanfile.py template
- `@conan-test` - Generate test_package
- `@conan-profile` - Create Conan profile
- `@conan-lockfile` - Generate lockfile

### Python Development
- `@python-type-hints` - Add type hints
- `@python-docstring` - Generate docstrings
- `@python-test` - Create pytest tests
- `@python-lint` - Run linting and fixes

### Debugging & Analysis
- `@debug` - Add debugging code
- `@trace` - Add execution tracing
- `@profile` - Add performance profiling
- `@security` - Security analysis
- `@performance` - Performance analysis

## Cursor Rules Usage

### In .cursor/rules/
Place `.mdc` files with rules like:
```markdown
# Rule Name
Description of the rule

## Code Style
- Use black formatting
- Follow PEP 8
- Add type hints

## Testing
- Write unit tests
- Use pytest
- Aim for 90% coverage
```

### Rule Activation
- Rules are automatically loaded from `.cursor/rules/`
- Use `@rule-name` to reference specific rules
- Combine multiple rules with `@rule1 @rule2`

## Conan Python Workflow

### 1. Create Package
```bash
@conan-create-basic
```

### 2. Add Dependencies
```python
def requirements(self):
    self.requires("fmt/10.1.1")
    self.requires("spdlog/1.12.0")
```

### 3. Generate Tests
```bash
@conan-test-basic
```

### 4. Build Package
```bash
conan create . --build=missing
```

### 5. Test Package
```bash
conan test test_package mypackage/1.0.0@user/channel
```

## Best Practices

### Code Quality
- Use `@python-lint` regularly
- Add `@python-type-hints` for all functions
- Generate `@python-test` for new features

### Conan Development
- Use `@conan-create` for new packages
- Apply `@conan-best-practices` for optimization
- Use `@conan-security` for security checks

### Documentation
- Use `@document` for API documentation
- Add `@python-docstring` for functions
- Generate `@explain` for complex code

## Quick Tips

1. **Use Cursor's AI**: Ask questions directly in chat
2. **Combine Commands**: `@conan-create @python-test @document`
3. **Custom Rules**: Create your own `.mdc` files
4. **Context Awareness**: Cursor understands your codebase
5. **Iterative Development**: Use commands to refine code

## Example Workflow

```bash
# 1. Create new Conan package
@conan-create-basic

# 2. Add Python integration
@conan-create-python

# 3. Generate tests
@conan-test-python

# 4. Add documentation
@document

# 5. Optimize
@conan-best-practices

# 6. Security check
@conan-security
```

Remember: Cursor's AI is context-aware and learns from your codebase. Use these commands as starting points and let the AI help you customize them for your specific needs.