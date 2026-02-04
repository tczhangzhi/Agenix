# Agenix Documentation

A lightweight AI coding agent.

## Documentation

### Getting Started

The Quick Start guide covers installation and first steps and can be found in the main README. The CLI Reference provides a complete command-line guide in `cli.md`. The SDK Documentation explains how to use Agenix as a Python library in `sdk.md`.

### Core Concepts

The Skills Guide explains the progressive disclosure system for specialized knowledge in `skills.md`. The Extensions Guide covers building custom tools, commands, and UI in `EXTENSIONS.md`. Session Management describes working with conversation sessions in `sessions.md`. The Settings Reference documents configuration options in `settings.md`.

### API Documentation

The API Reference contains auto-generated API documentation created with pdoc, available at `api/index.html`.

## Quick Links

### For Users

If you're using Agenix, start with Installation in the README, then learn the command-line interface in the CLI Reference, explore available commands in Interactive Commands, and configure Agenix through Settings.

### For Developers

If you're building with Agenix, start with the SDK Quick Start, review the API Reference, explore code examples in the examples directory, and learn to extend Agenix through the Extensions Guide.

### For Power Users

Advanced topics include the Skills System for creating custom skills, Session Format for understanding sessions, and Extension Development for building extensions.

## Documentation by Topic

### Command Line Usage

Topics include CLI Options, Usage Modes, Environment Variables, and Examples, all documented in `cli.md`.

### Programmatic Usage

Topics include Creating Sessions, Sending Prompts, Message Management, and Integration Patterns, all documented in `sdk.md`.

### Skills

Topics include Built-in Skills, Creating Skills, Skill Format, and Best Practices, all documented in `skills.md`.

### Extensions

Topics include Extension API, Event System, Custom Tools, and Examples, all documented in `EXTENSIONS.md`.

### Configuration

Topics include Settings Files, All Options, Environment Variables, and Multi-Project Setup, all documented in `settings.md`.

### Sessions

Topics include Storage Format, Working with Sessions, Session Operations, and Best Practices, all documented in `sessions.md`.

## Common Tasks

### How do I...

**...run Agenix in interactive mode?**
```bash
agenix
```
See the CLI Reference for interactive mode details.

**...use Agenix in my Python code?**
```python
from agenix import create_session
session = await create_session()
```
See the SDK Quick Start for details.

**...create a custom skill?**

Create `~/.agenix/skills/my-skill/SKILL.md` with frontmatter and instructions. See the Creating Skills section for details.

**...build an extension?**

Create a Python module with `async def setup(agenix)` function. See the Extensions Guide for details.

**...continue a previous conversation?**
```bash
agenix --continue
```
See Session Management for details.

**...change the default model?**

In `~/.agenix/settings.json`:
```json
{"model": "gpt-4"}
```
See the Settings Reference for model configuration details.

**...disable extensions?**
```bash
agenix --no-extensions
```
See CLI Options for details.

**...use a custom API endpoint?**
```bash
agenix --base-url https://my-api.com/v1
```
See the CLI Reference for details.

## Examples

### CLI Examples

```bash
# Interactive mode
agenix

# Direct message
agenix "List all Python files"

# Use GPT-4
agenix --model gpt-4 "Complex task"

# Custom working directory
agenix --working-dir ~/project "Analyze code"

# Continue last session
agenix --continue
```

### SDK Examples

```python
import asyncio
from agenix import create_session

async def main():
    session = await create_session(model="gpt-4o")
    response = await session.prompt("What files are here?")
    print(response)
    await session.close()

asyncio.run(main())
```

More examples are available in the `examples/` directory.

## Architecture

### Core Components

```
agenix/
├── core/
│   ├── agent.py         # Agent runtime & tool loop
│   ├── llm.py           # LLM provider interfaces
│   ├── messages.py      # Message types & events
│   ├── session.py       # Session management
│   └── skills.py        # Skills system
├── tools/
│   ├── read.py          # File reading
│   ├── write.py         # File writing
│   ├── edit.py          # File editing
│   ├── bash.py          # Shell execution
│   └── grep.py          # Code search
├── extensions/
│   ├── types.py         # Extension API types
│   ├── loader.py        # Extension loading
│   └── runner.py        # Extension execution
└── ui/
    └── cli.py           # Terminal UI
```

### Data Flow

```
User Input
    ↓
Agent Loop
    ↓
LLM Provider → Stream Events
    ↓
Tool Execution → Results
    ↓
Extension Hooks
    ↓
Session Save
```

## Contributing

See `CHANGELOG.md` for version history.