# Agenix

A lightweight AI coding agent powered by LLMs.

## Key Features

1. **Easy-to-Use Python Library** - Simple SDK that works as both CLI tool and importable library
2. **Agent Loop with Tool Execution** - Autonomous REPL loop where agent calls tools and continues until task completion
3. **Simple Tools Without MCP** - Four core tools (Read, Write, Edit, Bash) + Grep, no MCP dependencies
4. **Progressive Disclosure Skills** - Skills loaded on-demand to keep context minimal until needed
5. **Extension System** - Hot-reloadable extensions for custom tools, commands, and event handlers

## Installation

### From PyPI

```bash
pip install agenix
```

### From Source

```bash
git clone https://github.com/tczhangzhi/agenix.git
cd agenix
pip install -e .
```

### Using Conda

```bash
conda install -c tczhangzhi agenix
```

## Quick Start

### Setup API Keys

```bash
export OPENAI_API_BASE="https://api.openai.com/v1"
export OPENAI_API_KEY="your-key-here"
```

### Usage

```bash
# Interactive mode (enter TUI)
agenix

# Direct message
agenix "Read the README.md file and summarize it"

# Use specific model
agenix --model claude-3-5-sonnet-20241022 "analyze this code"

# Specify working directory
agenix --working-dir /path/to/project

# Load a previous session
agenix --session 20240101_120000

# Custom system prompt
agenix --system-prompt "You are a Python expert"

# Both python -m and agenix command work
python -m agenix "your message"
```

### Interactive Commands

- `/help` - Show help message
- `/clear` - Clear conversation history
- `/sessions` - List saved sessions
- `/load <session_id>` - Load a session
- `/quit` or `/exit` - Exit the program

## Programmatic SDK

Use agenix as a library in your Python applications:

```python
import asyncio
from agenix import create_session

async def main():
    # Create a session
    session = await create_session(
        api_key="your-openai-api-key",
        model="gpt-4o",
        working_dir="."
    )

    # Send prompts
    response = await session.prompt("What files are in the current directory?")
    print(response)

    # Continue conversation
    response = await session.prompt("Can you read the README?")
    print(response)

    # Get conversation history
    messages = session.get_messages()
    print(f"Conversation has {len(messages)} messages")

    # Clean up
    await session.close()

if __name__ == "__main__":
    asyncio.run(main())
```


## Extensions

Extend agenix with custom tools, commands, and event handlers.

### Extension Locations

- **Global**: `~/.agenix/extensions/`
- **Project**: `.agenix/extensions/`

### Example Extension

```python
# ~/.agenix/extensions/weather.py
from agenix.extensions import ToolDefinition

async def setup(agenix):
    """Extension setup function."""

    async def get_weather(params, ctx):
        city = params["city"]
        # Fetch weather data...
        return f"Weather in {city}: Sunny, 72°F"

    # Register custom tool
    agenix.register_tool(ToolDefinition(
        name="get_weather",
        description="Get current weather for a city",
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        },
        execute=get_weather
    ))
```

### Event Handlers

```python
# .agenix/extensions/logger.py
from agenix.extensions import EventType

async def setup(agenix):
    @agenix.on(EventType.TOOL_CALL)
    async def log_tool_calls(event, ctx):
        print(f"Tool called: {event.tool_name}")
```


## Agent Skills

Agenix supports progressive disclosure of specialized knowledge through Agent Skills.

Skills are automatically loaded from:
1. **Default**: `agenix/default-skills/` (bundled)
2. **User**: `~/.agenix/skills/` (global)
3. **Project**: `.agenix/skills/` (local, highest priority)

Built-in skills:
- `pdf` - PDF manipulation and extraction
- `xlsx` - Excel spreadsheet operations
- `docx` - Word document processing
- `pptx` - PowerPoint presentations
- `browser-use` - Web automation
- `find-skills` - Skill discovery
- `skill-creator` - Skill creation guide


## Documentation

Full documentation is available at **[https://agenix.readthedocs.io](https://agenix.readthedocs.io/en/latest/)**

## Links

- **PyPI**: [https://pypi.org/project/agenix/](https://pypi.org/project/agenix/)
- **Conda**: [https://anaconda.org/tczhangzhi/agenix](https://anaconda.org/tczhangzhi/agenix)

## Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agenix tests/

# Or use make
make test
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/tczhangzhi/agenix.git
cd agenix
make dev  # or: pip install -e .[dev]
```

### Common Commands

```bash
make help       # Show all commands
make install    # Install in development mode
make test       # Run tests
make clean      # Clean build artifacts
make build      # Build distribution
make upload     # Upload to PyPI
```