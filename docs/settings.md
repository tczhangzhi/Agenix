# Settings Reference

Configuration options for Agenix.

## Table of Contents

- [Overview](#overview)
- [Configuration Files](#configuration-files)
- [Settings Options](#settings-options)
- [Environment Variables](#environment-variables)
- [Examples](#examples)

## Overview

Agenix can be configured through:
1. Environment variables
2. Command-line arguments

Currently, Agenix does not support configuration files. All settings must be passed via environment variables or command-line options.

## Settings Options

### Model Configuration

Control which LLM model to use via command-line options.

#### --model
**Type**: string
**Default**: `"gpt-4o"`

Which LLM model to use.

```bash
agenix --model gpt-4o
```

Supported models:
- OpenAI: `gpt-4o`, `gpt-4`, `gpt-3.5-turbo`
- Anthropic: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`

#### --api-key
**Type**: string
**Default**: null (reads from environment)

API key for authentication. Prefer environment variables for security.

```bash
agenix --api-key "sk-..."
```

⚠️ **Security Warning**: Don't commit API keys to version control.

#### --base-url
**Type**: string
**Default**: null (uses provider default)

Custom API endpoint for OpenAI-compatible providers.

```bash
agenix --base-url "https://api.openai.com/v1"
```

### Agent Configuration

#### --max-turns
**Type**: integer
**Default**: 100

Maximum conversation turns per prompt.

```bash
agenix --max-turns 100
```

Lower values reduce costs but may stop before completing complex tasks.

#### --working-dir
**Type**: string
**Default**: `"."`

Working directory for file operations.

```bash
agenix --working-dir "/path/to/project"
```

#### --system-prompt
**Type**: string
**Default**: null (uses built-in prompt)

Custom system prompt to override defaults.

```bash
agenix --system-prompt "You are a Python expert..."
```

### Session Configuration

#### --session
**Type**: string
**Default**: null (creates new session)

Session ID to load.

```bash
agenix --session "20240101_120000"
```

## Environment Variables

Environment variables are the primary way to configure Agenix.

### Authentication

**OPENAI_API_KEY**
OpenAI API key.

```bash
export OPENAI_API_KEY="sk-..."
```

**ANTHROPIC_API_KEY**
Anthropic API key for Claude models.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**OPENAI_API_BASE** or **OPENAI_BASE_URL**
Custom API endpoint.

```bash
export OPENAI_API_BASE="https://api.openai.com/v1"
```

## Examples

### Development Setup

```bash
export OPENAI_API_KEY="sk-..."
agenix --model gpt-4o --max-turns 50
```

### Production Setup

```bash
export OPENAI_API_KEY="sk-..."
agenix --model gpt-4 --max-turns 20
```

### Custom Provider

```bash
export OPENAI_API_BASE="https://custom-api.example.com/v1"
export OPENAI_API_KEY="custom-key"
agenix --model custom-model --max-turns 100
```

### Project-Specific Configuration

```bash
# Project A
cd ~/projects/projectA
export OPENAI_API_KEY="sk-..."
agenix --model gpt-4 --system-prompt "You are a Python expert"

# Project B
cd ~/projects/projectB
export OPENAI_API_KEY="sk-..."
agenix --model claude-3-5-sonnet-20241022 --system-prompt "You are a TypeScript expert"
```

## Priority Order

Settings are applied in this order (later overrides earlier):

1. Built-in defaults
2. Environment variables
3. Command-line arguments

Example:

```bash
# Environment has: OPENAI_API_KEY="sk-123"
# Command-line has: --model gpt-4

# Result: Uses sk-123 (env) and gpt-4 (CLI)
```

## Configuration Tips

### Security

1. **Never commit API keys**: Use environment variables
2. **Use shell configuration**: Add exports to `.bashrc` or `.zshrc`

```bash
# ~/.bashrc
export OPENAI_API_KEY="sk-..."
```

### Performance

1. **Lower max_turns**: Reduce for simple tasks
2. **Choose right model**: Use `gpt-4o` for speed, `gpt-4` or Claude for complex reasoning

### Organization

1. **Use shell scripts**: Create project-specific scripts

```bash
#!/bin/bash
# ~/projects/myapp/run-agenix.sh
export OPENAI_API_KEY="sk-..."
cd ~/projects/myapp
agenix --model gpt-4 --system-prompt "You are a Python expert" "$@"
```

## Troubleshooting

### API Key Not Found

Check environment variables are set:
```bash
echo $OPENAI_API_KEY
```

### Wrong Model Used

Check which model is being used:
```bash
agenix --model gpt-4o "test"  # Explicitly set model
```

### Session Not Saving

Sessions auto-save to `~/.agenix/sessions/`. Check the directory exists:
```bash
ls ~/.agenix/sessions/
```

## Next Steps

- [CLI Reference](cli.md) - Command-line usage
- [SDK Documentation](sdk.md) - Programmatic usage
- [Skills Guide](skills.md) - Skill system
- [Extensions Guide](../EXTENSIONS.md) - Extension development
