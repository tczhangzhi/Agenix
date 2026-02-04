# Agenix Development Guidelines

This document defines development standards and best practices for the Agenix project.

## Core Principles

### 1. Test-Driven Development (TDD)

**All new features must include tests**

Every new feature requires corresponding unit tests. Write failing tests before fixing bugs, then make them pass. Ensure all tests pass during refactoring. The test coverage goal for core features is greater than 80%.

### 2. Documentation Synchronization

**Code and documentation must stay in sync**

New features must update relevant documentation. API changes must update API documentation. Example code must be runnable and tested. Use clear English in all code and documentation.

### 3. Code Quality Standards

**Keep code clean and maintainable**

Follow Python PEP 8 standards. Use Type Hints. All functions and classes must have docstrings. Avoid over-engineering and keep it simple (KISS principle).

## Testing Standards

### Test File Organization

```
tests/
├── core/           # Core module tests
│   ├── test_agent.py
│   ├── test_llm.py
│   ├── test_messages.py
│   └── test_session.py
├── tools/          # Tool tests
│   ├── test_read.py
│   ├── test_write.py
│   └── test_bash.py
└── ui/             # UI tests
    └── test_cli.py
```

### Test Naming Conventions

```python
class TestFeatureName:
    """Test cases for FeatureName."""

    def test_basic_functionality(self):
        """Test basic usage of feature."""
        pass

    def test_edge_case_empty_input(self):
        """Test handling of empty input."""
        pass

    def test_error_handling_invalid_param(self):
        """Test error handling for invalid parameters."""
        pass
```

### Tests Must Include

Tests should cover four main areas. First, happy path tests verify normal usage scenarios. Second, edge case tests cover boundary conditions. Third, error handling tests verify exceptional situations. Fourth, integration tests verify module interactions.

### Test Template

```python
"""Test suite for module_name.

This module contains unit tests for [feature description].
"""

import pytest
from agenix.core.module_name import FeatureName


class TestFeatureName:
    """Test cases for FeatureName class."""

    def test_feature_basic_usage(self):
        """Test basic usage of FeatureName.

        Verify that the basic functionality works as expected.
        """
        # Arrange
        feature = FeatureName(param="value")

        # Act
        result = feature.method()

        # Assert
        assert result == expected_value

    def test_feature_edge_case(self):
        """Test edge case with empty input.

        Verify handling of empty input.
        """
        feature = FeatureName()
        result = feature.method("")
        assert result is not None

    def test_feature_error_handling(self):
        """Test error handling for invalid input.

        Verify exception handling for invalid input.
        """
        feature = FeatureName()
        with pytest.raises(ValueError):
            feature.method(invalid_param)
```

## Documentation Standards

### Documentation File Organization

```
docs/
├── README.md           # Documentation overview
├── cli.md              # CLI usage guide
├── sdk.md              # SDK API documentation
├── skills.md           # Skills system documentation
├── extensions.md       # Extension system documentation
├── sessions.md         # Session management documentation
├── settings.md         # Configuration options documentation
└── api/                # Auto-generated API documentation
```

### When to Update Documentation

When adding a new feature, update the related module documentation and README. For example, adding a new tool requires updating `docs/tools.md`. When making API changes, update the SDK documentation. Modifying a function signature requires updating `docs/sdk.md`. For CLI changes, update the CLI documentation. Adding a CLI parameter requires updating `docs/cli.md`. When adding configuration options, update the settings documentation. Adding a config option requires updating `docs/settings.md`. For bug fixes, update the CHANGELOG by adding the fix description in the `[Unreleased]` section.

### Feature Documentation Template

```markdown
## Feature Name

### Overview

Brief description of the feature and its use cases.

### Quick Start

\`\`\`python
# Simplest usage example
from agenix import feature

result = feature.method()
print(result)
\`\`\`

### Detailed Description

#### Parameters

- `param1` (str): Description of parameter 1
- `param2` (int, optional): Description of parameter 2, default is 10

#### Return Value

Description of return value and its type.

#### Examples

\`\`\`python
# Example 1: Basic usage
example1()

# Example 2: Advanced usage
example2()
\`\`\`

### Notes

- Important notes about usage
- Known limitations

### Related Links

- [Related feature](link.md)
```

### Docstring Standards

```python
def function_name(param1: str, param2: int = 10) -> bool:
    """Brief description of the function (one line).

    Detailed explanation of what the function does and how to use it.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2, default is 10

    Returns:
        Description of return value

    Raises:
        ValueError: When ValueError is raised
        TypeError: When TypeError is raised

    Example:
        >>> function_name("test", 20)
        True

    Note:
        Important notes about usage
    """
    pass
```

## Development Workflow

### 1. Starting New Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/feature-name

# 2. Create corresponding test file in tests/
touch tests/core/test_new_feature.py

# 3. Write failing tests (TDD)
# Edit test_new_feature.py

# 4. Implement feature until tests pass
# Edit agenix/core/new_feature.py

# 5. Run tests
pytest tests/core/test_new_feature.py -v

# 6. Update documentation
# Edit docs/relevant-doc.md

# 7. Commit code
git add .
git commit -m "feat: add new feature with tests and docs"
```

### 2. Fixing Bugs

```bash
# 1. Create bug branch
git checkout -b fix/bug-description

# 2. Write test that reproduces the bug (test should fail)
# Add test in corresponding test_*.py

# 3. Fix bug until test passes
# Edit source code

# 4. Run all tests to ensure nothing else broke
pytest tests/ -v

# 5. Update CHANGELOG.md
# Add bug fix description in [Unreleased] section

# 6. Commit code
git commit -m "fix: description of bug fix"
```

### 3. Refactoring Code

```bash
# 1. Ensure all existing tests pass
pytest tests/ -v

# 2. Perform refactoring
# Edit code

# 3. Run tests after each small change
pytest tests/ -v

# 4. Update tests if needed to reflect new implementation
# But don't change public API behavior

# 5. Ensure all tests pass
pytest tests/ -v

# 6. Commit code
git commit -m "refactor: improve code structure"
```

## Pre-Commit Checklist

Before committing code, ensure you complete the following checks.

For code quality, verify that the code follows PEP 8 standards, all functions and classes have docstrings, type annotations are used, there are no unused imports or variables, and no print() debug statements remain.

For testing, ensure new features have corresponding unit tests, all tests pass when running `pytest tests/ -v`, tests cover normal, edge, and exceptional cases, and tests have clear docstrings.

For documentation, confirm that relevant docs/ documentation is updated, example code is runnable, docstrings are updated for API changes, and CHANGELOG.md is updated for bug fixes.

For Git, ensure commit messages follow conventions, no sensitive information is committed (such as API keys), and no large files or temporary files are committed.

## Commit Message Conventions

Use Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type Categories

The type categories are: `feat` for new features, `fix` for bug fixes, `docs` for documentation updates, `test` for test-related changes, `refactor` for code refactoring with no functional change, `style` for code formatting with no functional impact, `perf` for performance optimization, and `chore` for build or tool related changes.

### Examples

```bash
# New feature
git commit -m "feat(tools): add image recognition support with tests and docs"

# Bug fix
git commit -m "fix(session): fix image content serialization issue

- Add proper ImageContent handling in _content_to_dict
- Add _content_from_dict method for deserialization
- Update tests to verify image persistence"

# Documentation
git commit -m "docs(sdk): add multimodal content usage examples"

# Tests
git commit -m "test(core): add tests for edge cases in message handling"
```

## Code Review Points

### Reviewer Checklist

Reviewers should verify that code logic is correct and clear, there are adequate unit tests, tests cover critical paths, documentation is updated, no new security issues are introduced, performance impact is acceptable, and the changes are backward compatible or include a migration guide.

### Common Issues

Bad practices include code without type annotations, missing documentation, and missing tests:

```python
# No type annotations
def process_data(data):
    return data.strip()

# No documentation
# No tests
```

Good practices include proper type annotations, comprehensive documentation, and corresponding tests:

```python
def process_data(data: str) -> str:
    """Process input data by stripping whitespace.

    Args:
        data: Input string

    Returns:
        Processed string

    Example:
        >>> process_data("  hello  ")
        "hello"
    """
    return data.strip()

# Corresponding test
def test_process_data():
    """Test data processing with whitespace."""
    assert process_data("  hello  ") == "hello"
    assert process_data("") == ""
```

## Development Tools

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific module
pytest tests/core/test_session.py -v

# Run specific test
pytest tests/core/test_session.py::TestSessionManager::test_save_message -v

# View test coverage
pytest tests/ --cov=agenix --cov-report=html
```

### Code Checks

```bash
# Type checking
mypy agenix/

# Code format checking
flake8 agenix/

# Auto-format
black agenix/
```

### Generating Documentation

```bash
# Generate API documentation
pdoc --html --output-dir docs/api agenix/

# Preview documentation locally
python -m http.server -d docs/ 8000
# Visit http://localhost:8000
```

## Important Notes

### Performance Considerations

Avoid unnecessary file I/O. Use streaming for large files. Cache expensive computations. Avoid repeated calculations in loops.

### Security Considerations

Validate all user input. Don't log sensitive information. Use parameterized queries to prevent injection. Avoid executing unvalidated code.

### Compatibility

Maintain backward compatibility. Provide a migration guide for breaking changes. Use semantic versioning. Clearly mark breaking changes in the CHANGELOG.

## Learning Resources

### Testing

For testing guidance, refer to the pytest documentation at https://docs.pytest.org/ and Testing Best Practices at https://docs.python-guide.org/writing/tests/.

### Documentation

For documentation standards, refer to the Google Python Style Guide at https://google.github.io/styleguide/pyguide.html and Write the Docs at https://www.writethedocs.org/.

### Python Best Practices

For Python best practices, refer to PEP 8 at https://pep8.org/ and Type Hints documentation at https://docs.python.org/3/library/typing.html.

## Getting Help

If you have questions, first check existing code examples. Then read relevant documentation. Search existing Issues at https://github.com/tczhangzhi/agenix/issues. If needed, create a new Issue to ask for help.

---

**Remember: Good code = Function + Tests + Documentation**

Every commit should make the project better and more maintainable!