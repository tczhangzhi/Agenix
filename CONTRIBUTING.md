# Contributing to Agenix

Thank you for considering contributing to Agenix! This document will help you understand how to participate in project development.

## 🚀 Quick Start

### 1. Fork and Clone the Project

```bash
# Fork the project to your GitHub account
# Then clone it locally
git clone https://github.com/YOUR_USERNAME/agenix.git
cd agenix

# Add upstream repository
git remote add upstream https://github.com/tczhangzhi/agenix.git
```

### 2. Set Up Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Or use conda
conda env create -f environment.yml
conda activate agenix

# Verify installation
pytest tests/ -v
```

### 3. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

## 📋 Development Standards

### Core Principles

We follow three core principles:

1. **Test-Driven Development (TDD)** - All new features must have tests
2. **Documentation Synchronization** - Code changes must update documentation
3. **Code Quality Standards** - Keep code clean and maintainable

For detailed development standards, see: [Development Guidelines](.claude/development-guidelines.md)

### Pre-Commit Checklist

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Code follows PEP 8: `flake8 agenix/`
- [ ] Added necessary tests
- [ ] Updated relevant documentation
- [ ] Commit message follows conventions

## 🧪 Testing Guide

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific module
pytest tests/core/ -v

# View test coverage
pytest tests/ --cov=agenix --cov-report=html
```

### Writing Tests

Each new feature needs tests that include:

1. **Normal cases** - Feature works properly
2. **Edge cases** - Boundary condition handling
3. **Exception cases** - Error handling

Example:

```python
"""Test suite for new feature."""

import pytest
from agenix.core.feature import NewFeature


class TestNewFeature:
    """Test cases for NewFeature."""

    def test_basic_usage(self):
        """Test basic functionality."""
        feature = NewFeature()
        result = feature.process("input")
        assert result == "expected"

    def test_edge_case_empty(self):
        """Test handling of empty input."""
        feature = NewFeature()
        result = feature.process("")
        assert result is not None

    def test_error_invalid_input(self):
        """Test error handling."""
        feature = NewFeature()
        with pytest.raises(ValueError):
            feature.process(None)
```

## 📚 Documentation Guide

### When to Update Documentation

| Change Type | Documentation to Update |
|------------|------------------------|
| New Feature | `docs/` relevant documentation |
| API Change | `docs/sdk.md` + docstrings |
| CLI Change | `docs/cli.md` |
| Bug Fix | `CHANGELOG.md` |

### Documentation Structure

```
docs/
├── README.md       # Documentation overview
├── cli.md          # CLI usage guide
├── sdk.md          # SDK API documentation
├── skills.md       # Skills system
├── extensions.md   # Extension development
├── sessions.md     # Session management
└── settings.md     # Configuration options
```

### Docstring Standard

```python
def function_name(param: str) -> bool:
    """Brief description of the function (one line).

    Detailed explanation of the function's purpose and usage.

    Args:
        param: Parameter description

    Returns:
        Return value description

    Raises:
        ValueError: Exception description

    Example:
        >>> function_name("test")
        True
    """
    pass
```

## 🔄 Workflow

### Developing New Features

```bash
# 1. Sync latest code
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Write tests (TDD)
vim tests/core/test_my_feature.py

# 4. Implement feature
vim agenix/core/my_feature.py

# 5. Run tests
pytest tests/ -v

# 6. Update documentation
vim docs/relevant-doc.md

# 7. Commit code
git add .
git commit -m "feat: add my feature with tests and docs"

# 8. Push to your fork
git push origin feature/my-feature

# 9. Create Pull Request
# Create PR on GitHub
```

### Fixing Bugs

```bash
# 1. Create bug branch
git checkout -b fix/bug-description

# 2. Write test to reproduce bug
vim tests/test_relevant.py

# 3. Fix bug
vim agenix/relevant_module.py

# 4. Ensure tests pass
pytest tests/ -v

# 5. Update CHANGELOG
vim CHANGELOG.md

# 6. Commit and create PR
git commit -m "fix: description of bug fix"
git push origin fix/bug-description
```

## 📝 Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Type Categories

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation update
- `test`: Test related
- `refactor`: Code refactoring
- `style`: Code formatting
- `perf`: Performance optimization
- `chore`: Build/tool related

### Examples

```bash
# New feature
feat(tools): add image recognition support

Add support for reading and analyzing images using multimodal LLMs.
Includes tests and documentation.

# Bug fix
fix(session): fix image content serialization

Images were not being saved in session files. Added proper handling
for ImageContent in serialization/deserialization.

# Documentation
docs(sdk): update API examples with async/await syntax

# Testing
test(core): add edge case tests for message handling
```

## 🔍 Code Review

### Pull Request Guidelines

When creating a PR, ensure:

1. **Clear title** - Use Conventional Commits format
2. **Complete description** - Explain reason and content of changes
3. **Tests pass** - CI must be green
4. **Documentation updated** - Relevant docs updated
5. **No conflicts** - Merge conflicts resolved

### PR Template

```markdown
## Description

Brief description of this PR's purpose and content.

## Change Type

- [ ] New feature (feat)
- [ ] Bug fix (fix)
- [ ] Documentation (docs)
- [ ] Testing (test)
- [ ] Refactoring (refactor)
- [ ] Performance (perf)

## Testing

- [ ] Added new tests
- [ ] All tests pass
- [ ] Manual testing completed

## Documentation

- [ ] Updated relevant documentation
- [ ] Updated CHANGELOG.md
- [ ] Updated example code

## Screenshots (if applicable)

## Related Issues

Closes #123
```

## 🎨 Code Style

### Python Code Standards

- Follow [PEP 8](https://pep8.org/)
- Use Type Hints
- Every function/class needs docstring
- Keep functions short (<50 lines)
- Use descriptive variable names

### Example

```python
from typing import List, Optional


def process_messages(
    messages: List[str],
    max_length: Optional[int] = None
) -> List[str]:
    """Process message list and return processed results.

    Args:
        messages: List of messages to process
        max_length: Maximum length limit, None for unlimited

    Returns:
        List of processed messages

    Example:
        >>> process_messages(["hello", "world"])
        ["HELLO", "WORLD"]
    """
    result = [msg.upper() for msg in messages]

    if max_length:
        result = [msg[:max_length] for msg in result]

    return result
```

## 🐛 Reporting Bugs

### Bug Report Template

Please create a bug report in [GitHub Issues](https://github.com/tczhangzhi/agenix/issues) including:

1. **Environment Information**
   - OS: [e.g., macOS 14.0]
   - Python Version: [e.g., 3.11.5]
   - Agenix Version: [e.g., 0.1.0]

2. **Steps to Reproduce**
   ```bash
   agenix "your command"
   ```

3. **Expected Behavior**
   Describe what you expected to happen

4. **Actual Behavior**
   Describe what actually happened

5. **Error Logs**
   ```
   Paste error messages
   ```

6. **Screenshots (if applicable)**

## 💡 Feature Requests

### Feature Request Template

1. **Feature Description**
   Clear description of desired feature

2. **Use Case**
   What problem does this feature solve?

3. **Proposed Implementation**
   If you have ideas, describe them

4. **Alternative Solutions**
   Have you considered other approaches?

## 🤝 Community

### Code of Conduct

- Respect all contributors
- Accept constructive criticism
- Focus on project's best interests
- Show empathy

### Getting Help

- Review [Documentation](docs/README.md)
- Search existing [Issues](https://github.com/tczhangzhi/agenix/issues)
- Join discussion forum (if available)
- Create new Issue to ask questions

## 📄 License

By contributing code, you agree that your contributions will be licensed under the [MIT License](LICENSE).

## 🙏 Acknowledgements

Thank you to all contributors who have made Agenix better!

Your contributions make this project better. ❤️

---

## FAQ

### Q: I'm a beginner, can I contribute?

A: Absolutely! We welcome contributors of all levels. You can start with simple tasks like:
- Improving documentation
- Fixing typos
- Adding tests
- Reporting bugs

Look for issues labeled `good first issue`.

### Q: How long does PR review take?

A: We try to review PRs as quickly as possible, typically within 1-3 days. If there's no response after a week, you can @ maintainers in the PR.

### Q: What if tests fail?

A: First run tests locally:
```bash
pytest tests/ -v
```
If they pass locally but fail in CI, it may be an environment difference. Check CI logs to find the cause.

### Q: Should I open an Issue first or submit a PR directly?

A: For large feature changes, it's recommended to open an Issue first for discussion. Small bug fixes or documentation improvements can go straight to PR.

### Q: How do I keep my fork in sync?

A: Regularly sync with upstream:
```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

---

Thank you for reading this far! Looking forward to your contributions! 🎉
