# Agenix Project - Claude Development Assistant Instructions

This file provides automated instructions and context information for Claude to assist with project development.

## Project Overview

**Agenix** is a lightweight AI coding agent framework supporting multimodal content processing and tool extensions.

The primary language is Python 3.11+. The architecture follows a modular design with plugin and extension support. The test framework is pytest, and documentation tools include pdoc and Markdown.

## Development Instructions

### Mandatory Requirements

When developing new features or fixing bugs, Claude **MUST** follow these requirements.

**Write Tests**: Every new feature must have corresponding unit tests. Test files go in `tests/` under the corresponding module directory. Tests must include normal cases, edge cases, and exceptional cases. Run `pytest tests/ -v` to ensure all tests pass.

**Update Documentation**: New features must update relevant documentation in `docs/`. API modifications must update docstrings. CLI changes must update `docs/cli.md`. Bug fixes must update `CHANGELOG.md`.

**Code Quality**: Use Type Hints. Every function and class must have a docstring in English. Follow PEP 8 standards. Keep code simple following the KISS principle.

## Project Structure

```
agenix/
├── agenix/
│   ├── core/          # Core modules
│   │   ├── agent.py       # Agent runtime
│   │   ├── llm.py         # LLM provider interfaces
│   │   ├── messages.py    # Message type definitions
│   │   ├── session.py     # Session management
│   │   └── skills.py      # Skills system
│   ├── tools/         # Built-in tools
│   │   ├── base.py        # Tool base class
│   │   ├── read.py        # File reading
│   │   ├── write.py       # File writing
│   │   ├── edit.py        # File editing
│   │   ├── bash.py        # Shell execution
│   │   └── grep.py        # Code search
│   ├── extensions/    # Extension system
│   └── ui/            # User interface
│       └── cli.py         # Command-line interface
├── tests/             # Test files
│   ├── core/          # Core module tests
│   ├── tools/         # Tool tests
│   └── ui/            # UI tests
├── docs/              # Documentation
│   ├── README.md      # Documentation overview
│   ├── cli.md         # CLI documentation
│   ├── sdk.md         # SDK documentation
│   ├── skills.md      # Skills documentation
│   ├── extensions.md  # Extension documentation
│   └── ...
└── examples/          # Example code
```

## Workflow Templates

### New Feature Development Process

When a user requests "implement XXX feature", Claude should follow these steps.

#### 1. Planning Phase

```markdown
I will implement [feature name], including the following steps:

1. **Design** - Feature design and API design
2. **Tests** - Write test cases
3. **Implementation** - Implement feature code
4. **Documentation** - Update relevant documentation
5. **Verification** - Run tests to ensure passing

Starting implementation...
```

#### 2. Write Tests (TDD)

```python
# File: tests/core/test_new_feature.py
"""Test suite for new feature.

This module tests various usage scenarios of the new feature.
"""

import pytest
from agenix.core.new_feature import NewFeature


class TestNewFeature:
    """Test cases for NewFeature."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        feature = NewFeature()

        # Act
        result = feature.process("input")

        # Assert
        assert result == "expected"

    def test_edge_case_empty_input(self):
        """Test edge case with empty input."""
        feature = NewFeature()
        result = feature.process("")
        assert result is not None

    def test_error_handling(self):
        """Test error handling."""
        feature = NewFeature()
        with pytest.raises(ValueError):
            feature.process(None)
```

#### 3. Implement Feature

```python
# File: agenix/core/new_feature.py
"""New feature module."""

from typing import Optional


class NewFeature:
    """New feature class.

    Implements core logic for XXX functionality.

    Example:
        >>> feature = NewFeature()
        >>> feature.process("input")
        "output"
    """

    def process(self, data: Optional[str]) -> str:
        """Process input data.

        Args:
            data: Input data

        Returns:
            Processed result

        Raises:
            ValueError: When data is None

        Example:
            >>> feature = NewFeature()
            >>> feature.process("test")
            "PROCESSED: test"
        """
        if data is None:
            raise ValueError("data cannot be None")

        if not data:
            return ""

        return f"PROCESSED: {data}"
```

#### 4. Run Tests

```bash
pytest tests/core/test_new_feature.py -v
```

#### 5. Update Documentation

```markdown
# Add to docs/relevant-doc.md

## New Feature Name

### Overview

Brief description of the feature.

### Usage

\`\`\`python
from agenix.core.new_feature import NewFeature

feature = NewFeature()
result = feature.process("input")
print(result)
\`\`\`

### Parameters

- `data` (str): Input data

### Return Value

Returns processed string.

### Examples

\`\`\`python
# Example 1: Basic usage
feature = NewFeature()
result = feature.process("hello")

# Example 2: Error handling
try:
    feature.process(None)
except ValueError as e:
    print(f"Error: {e}")
\`\`\`
```

#### 6. Summary

```markdown
Completed implementation of [feature name]:

**Modified files:**
- `agenix/core/new_feature.py` - Implemented new feature
- `tests/core/test_new_feature.py` - Added tests
- `docs/relevant-doc.md` - Updated documentation

**Test results:**
- All tests pass

**Documentation updates:**
- Added usage examples and API description

Feature is ready for use!
```

### Bug Fix Process

When a user reports "XXX has a bug", Claude should follow these steps.

#### 1. Understand the Problem

```markdown
My understanding of the issue:
- **Symptoms**: [describe error]
- **Location**: [related files and line numbers]
- **Impact**: [scope of impact]

Starting fix...
```

#### 2. Write Reproduction Test

```python
# Add to corresponding test_*.py
def test_bug_reproduction(self):
    """Test to reproduce bug XXX.

    This test should fail until the bug is fixed.
    """
    # Code to reproduce bug
    result = buggy_function(input)
    assert result == expected  # Currently fails
```

#### 3. Fix Bug

```python
# Modify source code
def buggy_function(input):
    """Fixed function."""
    # Fix logic
    return corrected_result
```

#### 4. Verify Fix

```bash
pytest tests/test_buggy.py -v
```

#### 5. Update CHANGELOG

```markdown
# Add to [Unreleased] section in CHANGELOG.md

### Fixed
- Fixed bug in XXX feature, now correctly handles YYY cases
```

## Common Commands

### Test Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific module
pytest tests/core/ -v

# Run specific test
pytest tests/core/test_session.py::TestSessionManager::test_save_message -v

# View coverage
pytest tests/ --cov=agenix --cov-report=html
```

### Code Checks

```bash
# Type checking
mypy agenix/

# Code formatting
flake8 agenix/

# Auto-format
black agenix/
```

## Code Style Requirements

### Docstring Template

```python
def function_name(param1: str, param2: int = 10) -> bool:
    """Brief description of the function.

    Detailed explanation of the function's purpose and usage.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2, default is 10

    Returns:
        Description of return value

    Raises:
        ValueError: When to raise ValueError
        TypeError: When to raise TypeError

    Example:
        >>> function_name("test", 20)
        True

    Note:
        Important usage notes
    """
    pass
```

### Test Naming Conventions

```python
class TestFeatureName:
    """Test cases for FeatureName."""

    def test_basic_usage(self):
        """Test basic functionality."""
        pass

    def test_edge_case_empty_input(self):
        """Test edge case with empty input."""
        pass

    def test_error_invalid_param(self):
        """Test error handling for invalid parameters."""
        pass
```

## Special Notes

### Multimodal Content Handling

The project supports multimodal content including text and images. There are several important considerations.

**Use isinstance instead of hasattr**:

```python
# Good practice
if isinstance(item, ImageContent):
    process_image(item)

# Avoid duck typing
if hasattr(item, 'source'):
    process_image(item)
```

**Handle all content types during serialization**:

```python
def _content_to_dict(self, content):
    if isinstance(content, TextContent):
        return {"type": "text", "text": content.text}
    elif isinstance(content, ImageContent):
        return {"type": "image", "source": content.source}
    # Add other types...
```

**Maintain backward compatibility**: Text-only content can return strings directly, while mixed content returns lists.

### Session Management

Session data is stored in the `~/.agenix/` directory. It uses JSONL format with one message per line and supports serialization and deserialization of all content types.

### LLM Providers

The framework supports multiple LLM providers including OpenAI (default), Anthropic Claude, and other OpenAI API-compatible services.

## Reference Documentation

For more detailed information, refer to the Complete Development Guidelines at `.claude/development-guidelines.md`, the Contributing Guide at `CONTRIBUTING.md`, and the Project Documentation at `docs/README.md`.

## Pre-Submission Checklist

Claude should confirm the following before completing tasks: the feature works correctly, all tests pass when running `pytest tests/ -v`, new tests cover new features, relevant documentation is updated, code has type annotations and docstrings, code follows style standards, and changes are backward compatible or provide a migration guide.

## Communication Style

When Claude completes a task, provide a clear summary:

```markdown
Task completed!

**Implementation content:**
- [Feature/fix description]

**Modified files:**
- `path/to/file1.py` - [modification description]
- `path/to/file2.py` - [modification description]
- `docs/doc.md` - [updated content]

**Test results:**
```bash
pytest tests/ -v
# [test output]
```

**Next steps:**
- [Optional follow-up improvements]
```

---

Remember: **Good code = Function + Tests + Documentation**

Claude must ensure every submission makes the project better and more maintainable!