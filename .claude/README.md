# Claude Configuration for Agenix Project

This directory contains Claude Code configuration for the Agenix project.

## Files

### `settings.local.json`

This file contains permission settings for Claude Code, including allowed commands and tools. It has been configured with broad development permissions.

### `instructions.md`

This file provides development guidelines and workflows for Claude, containing automated instructions for feature development and bug fixes. Code and comments are in English, while communication with users is in Chinese.

### `development-guidelines.md`

This file documents complete development standards and best practices, including testing standards, documentation requirements, and code quality guidelines. All content is in English.

## Configuration Status

### Permissions Enabled

Claude has been granted the following permissions:

Git operations include all git commands. Python and testing tools include python, pytest, pip, and conda. File operations include ls, cat, grep, find, wc, mkdir, rm, mv, and cp. Build tools include make, npm, node, and docker. Network tools include curl, wget, and WebFetch.

### Development Rules

All new features must include tests with unit tests providing good coverage, documentation with updated docs and docstrings, and code quality with type hints, PEP 8 compliance, and docstrings.

### Language Settings

Code is written in English. Comments are written in English. Documentation is written in English. Communication with users is in Chinese.

## Usage

Claude will automatically write tests before implementing features following TDD principles, update relevant documentation, follow code style guidelines, and provide clear summaries in Chinese.

## Quick Reference

### When adding a new feature:

```bash
# 1. Claude will create tests first
tests/core/test_new_feature.py

# 2. Then implement the feature
agenix/core/new_feature.py

# 3. Update documentation
docs/relevant-doc.md

# 4. Run tests to verify
pytest tests/ -v
```

### File modification pattern:

For every feature, expect changes to source code in `agenix/`, tests in `tests/`, and documentation in `docs/`.

## Verification

To verify the configuration is working, ask Claude to implement a new feature, check that tests are created first, verify documentation is updated, and confirm all code uses English with proper docstrings.

## Related Documents

For full standards, see the Development Guidelines at `development-guidelines.md`. For external contributors, see the Contributing Guide at `../CONTRIBUTING.md`. For user-facing docs, see the Project Documentation at `../docs/README.md`.

## Notes

All tests must pass before committing. Documentation must stay in sync with code. Use semantic versioning for releases. Follow Conventional Commits format.