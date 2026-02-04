# CLI Reference

Complete command-line reference for Agenix.

## Table of Contents

- [Quick Start](#quick-start)
- [Usage Modes](#usage-modes)
- [Command Line Options](#command-line-options)
- [Interactive Commands](#interactive-commands)
- [Environment Variables](#environment-variables)
- [Examples](#examples)

## Quick Start

```bash
# Install
pip install agenix

# Set API key
export OPENAI_API_KEY="sk-..."

# Run interactive mode
agenix

# Or direct message
agenix "List files in current directory"
```

## Usage Modes

### Interactive Mode

Default mode with rich TUI interface:

```bash
agenix
```

Features:
- Rich terminal UI with prompt_toolkit
- Full Unicode support (Chinese, Japanese, etc.)
- Real-time streaming responses
- Tool execution visualization
- Session auto-save

### Direct Message Mode

Process a single message and exit:

```bash
agenix "Your message here"
```

The agent will process the message and output the response, perfect for scripting.

### Python Module Mode

Run as a Python module:

```bash
python -m agenix "Your message"
```

## Command Line Options

### Model Configuration

```bash
--model <model_id>
```

Specify which LLM model to use. Examples:
- `gpt-4o` (default)
- `gpt-4`
- `claude-3-5-sonnet-20241022`
- `claude-3-opus-20240229`

```bash
--api-key <key>
```

API key for authentication. Alternatively, set via environment variables:
- `OPENAI_API_KEY` - For OpenAI models
- `ANTHROPIC_API_KEY` - For Claude models

```bash
--base-url <url>
```

Custom API endpoint for OpenAI-compatible APIs.

### Working Directory

```bash
--working-dir <path>
```

Set the working directory for file operations. Default: current directory.

Example:
```bash
agenix --working-dir /path/to/project "Analyze this codebase"
```

### System Prompt

```bash
--system-prompt <prompt>
```

Custom system prompt to override default instructions.

Example:
```bash
agenix --system-prompt "You are a Python expert specializing in Django"
```

### Session Management

```bash
--session <session_id>
```

Load a specific session to continue previous conversation.

Example:
```bash
agenix --session 20240101_120000
```

### Agent Configuration

```bash
--max-turns <number>
```

Maximum conversation turns per prompt. Default: 100.

Lower values save on API costs but may stop before complex tasks complete.

## Interactive Commands

Commands available in interactive mode:

- `/help` - Show help message and available tools
- `/clear` - Clear conversation history
- `/sessions` - List saved sessions
- `/load <session_id>` - Load a previous session
- `/quit` or `/exit` - Exit the program

## Environment Variables

### Required

**OPENAI_API_KEY** or **ANTHROPIC_API_KEY**

API key for your chosen provider.

```bash
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Optional

**OPENAI_API_BASE** or **OPENAI_BASE_URL**

Custom API endpoint for OpenAI-compatible providers.

```bash
export OPENAI_API_BASE="https://api.openai.com/v1"
```

## Examples

### Basic Usage

```bash
# Start interactive mode
agenix

# Direct message
agenix "What files are in this directory?"

# Use specific model
agenix --model gpt-4 "Review this code for bugs"
```

### Working with Projects

```bash
# Analyze a specific project
agenix --working-dir ~/projects/myapp "Summarize the codebase structure"

# Load previous session
agenix --session 20240101_120000
```

### Custom Configuration

```bash
# Use custom API endpoint
agenix --base-url https://my-api.com/v1 --api-key "my-key"

# Custom system prompt
agenix --system-prompt "You are a code reviewer" "Review main.py"

# Lower max turns for simple tasks
agenix --max-turns 10 "Quick task"
```

### Scripting

```bash
# One-liner for scripts
agenix "Generate a README for this project" > README.md

# Process multiple files
for file in *.py; do
    agenix "Add docstrings to $file"
done

# CI/CD integration
if agenix "Check code quality" | grep -q "issues found"; then
    exit 1
fi
```

### Model Selection

```bash
# Use GPT-4
agenix --model gpt-4 "Complex reasoning task"

# Use Claude
agenix --model claude-3-5-sonnet-20241022 "Long document analysis"

# Use GPT-4o (default, fastest)
agenix "Quick task"
```

## Tips

### Performance

- Use `gpt-4o` for fast, cost-effective tasks
- Use `gpt-4` or Claude Opus for complex reasoning
- Set `--max-turns` lower for simple tasks to reduce cost

### Session Management

- Sessions auto-save in `~/.agenix/sessions/`
- Organized by working directory
- Use `/sessions` in interactive mode to browse
- Load with `--session <id>` or `/load <id>`

### File Operations

- The agent has access to Read, Write, Edit, Bash, and Grep tools
- Always works relative to `--working-dir`
- Use Edit tool for surgical changes (find/replace)
- Use Write tool for creating new files

### Unicode Support

- Full support for Chinese, Japanese, Korean, and other multi-byte characters
- Uses prompt_toolkit for proper rendering
- Works correctly with emoji and special characters

## Troubleshooting

### API Key Not Found

```bash
Error: API key not found
```

**Solution**: Set the appropriate environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

### Unicode Display Issues

If you see garbled characters:

1. Ensure your terminal supports UTF-8
2. Set locale: `export LANG=en_US.UTF-8`
3. Use a modern terminal (iTerm2, Windows Terminal, etc.)

### Session Not Found

```bash
Error: Session not found
```

**Solution**: Use `/sessions` command in interactive mode to see available sessions:
```bash
agenix
> /sessions
```

### Tool Execution Errors

If bash commands fail:

1. Check working directory: `--working-dir`
2. Verify file permissions
3. Check if command exists in PATH

## Next Steps

- [SDK Documentation](sdk.md) - Use Agenix programmatically
- [Skills Guide](skills.md) - Progressive disclosure system
- [Extensions Guide](../EXTENSIONS.md) - Extend with custom functionality
- [Settings Reference](settings.md) - Configuration options
