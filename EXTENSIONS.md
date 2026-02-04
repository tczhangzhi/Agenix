# Agenix Extensions and SDK

This document covers the Extensions system and Programmatic SDK.

## Table of Contents

1. [Programmatic SDK](#programmatic-sdk)
2. [Extensions System](#extensions-system)
3. [Examples](#examples)

---

## Programmatic SDK

Agenix can be used as a library in your Python applications.

### Basic Usage

```python
import asyncio
from agenix import create_session

async def main():
    # Create a session
    session = await create_session(
        api_key="your-openai-api-key",
        model="gpt-4o",
        working_dir="/path/to/project"
    )

    # Send a prompt
    response = await session.prompt("What files are in the current directory?")
    print(response)

    # Continue conversation
    response = await session.prompt("Can you read the README?")
    print(response)

    # Get conversation history
    messages = session.get_messages()
    print(f"Conversation has {len(messages)} messages")

    # Clear history
    session.clear_messages()

    # Close session
    await session.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### API Reference

#### `create_session(**kwargs)` → `AgentSession`

Create a new agent session.

**Parameters:**
- `api_key` (str, optional): API key for LLM provider (or set `OPENAI_API_KEY` env var)
- `base_url` (str, optional): Custom API base URL
- `model` (str): Model to use (default: "gpt-4o")
- `system_prompt` (str, optional): Custom system prompt
- `working_dir` (str): Working directory for file operations (default: ".")
- `max_turns` (int): Maximum conversation turns per prompt (default: 10)
- `enable_extensions` (bool): Whether to load extensions (default: True)

**Returns:** `AgentSession` instance

#### `AgentSession.prompt(message: str)` → `str`

Send a message to the agent and get the response.

**Parameters:**
- `message` (str): User message/prompt

**Returns:** Agent's text response as string

#### `AgentSession.get_messages()` → `List[Message]`

Get conversation history.

**Returns:** List of messages in the conversation

#### `AgentSession.clear_messages()` → `None`

Clear conversation history.

#### `AgentSession.close()` → `None`

Close the session and cleanup resources.

---

## Extensions System

Extensions are Python modules that extend agenix with custom tools, commands, and event handlers.

### Extension Locations

Extensions are discovered from these locations (in order):

1. **Global**: `~/.agenix/extensions/`
2. **Project**: `.agenix/extensions/`

### Creating an Extension

Create a Python file with a `setup(agenix)` function:

```python
# ~/.agenix/extensions/my_extension.py
async def setup(agenix):
    """Extension setup function.

    Args:
        agenix: ExtensionAPI instance
    """
    # Register tools, commands, and event handlers here
    pass
```

### Extension API

#### Registering Custom Tools

```python
from agenix.extensions import ToolDefinition

async def setup(agenix):
    async def my_tool_execute(params, ctx):
        """Tool execution function.

        Args:
            params: Dictionary of parameters from LLM
            ctx: ExtensionContext instance

        Returns:
            String result to send back to LLM
        """
        input_text = params.get("input", "")
        # Do something with input
        return f"Processed: {input_text}"

    agenix.register_tool(ToolDefinition(
        name="my_tool",
        description="My custom tool for doing X",
        parameters={
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Input text to process"
                }
            },
            "required": ["input"]
        },
        execute=my_tool_execute
    ))
```

#### Registering Commands

```python
from agenix.extensions import CommandDefinition

async def setup(agenix):
    async def stats_handler(ctx, args):
        """Command handler function.

        Args:
            ctx: ExtensionContext instance
            args: Command arguments as string
        """
        # Access agent state
        message_count = len(ctx.messages)
        ctx.notify(f"Total messages: {message_count}", "info")

    agenix.register_command(CommandDefinition(
        name="stats",
        description="Show conversation statistics",
        handler=stats_handler
    ))
```

#### Event Handlers

```python
from agenix.extensions import EventType

async def setup(agenix):
    @agenix.on(EventType.AGENT_START)
    async def on_agent_start(event, ctx):
        """Called when agent loop starts.

        Args:
            event: AgentStartEvent instance
            ctx: ExtensionContext instance
        """
        print(f"Agent starting with prompt: {event.prompt}")

    @agenix.on(EventType.TOOL_CALL)
    async def on_tool_call(event, ctx):
        """Called before each tool execution.

        Args:
            event: ToolCallEvent instance
            ctx: ExtensionContext instance
        """
        print(f"Tool {event.tool_name} called with args: {event.args}")

    @agenix.on(EventType.TOOL_RESULT)
    async def on_tool_result(event, ctx):
        """Called after each tool execution.

        Args:
            event: ToolResultEvent instance
            ctx: ExtensionContext instance
        """
        print(f"Tool {event.tool_name} returned: {event.result}")
```

### Available Events

- `EventType.SESSION_START` - Session started
- `EventType.SESSION_END` - Session ended
- `EventType.AGENT_START` - Agent loop started
- `EventType.AGENT_END` - Agent loop ended
- `EventType.TURN_START` - Turn started
- `EventType.TURN_END` - Turn ended
- `EventType.TOOL_CALL` - Before tool execution
- `EventType.TOOL_RESULT` - After tool execution
- `EventType.USER_INPUT` - User input received

### Extension Context

The `ExtensionContext` object provides access to agent state:

```python
async def my_handler(event, ctx):
    # Access current messages
    messages = ctx.messages

    # Access agent instance
    agent = ctx.agent

    # Access working directory
    cwd = ctx.cwd

    # Access available tools
    tools = ctx.tools

    # Show notification
    ctx.notify("Something happened!", "info")
```

---

## Examples

### Example 1: Custom Deployment Tool

```python
# ~/.agenix/extensions/deploy.py
import subprocess
from agenix.extensions import ToolDefinition

async def setup(agenix):
    async def deploy_execute(params, ctx):
        environment = params.get("environment", "staging")

        # Run deployment
        result = subprocess.run(
            ["./deploy.sh", environment],
            cwd=ctx.cwd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return f"Deployment to {environment} successful!"
        else:
            return f"Deployment failed: {result.stderr}"

    agenix.register_tool(ToolDefinition(
        name="deploy",
        description="Deploy application to specified environment",
        parameters={
            "type": "object",
            "properties": {
                "environment": {
                    "type": "string",
                    "enum": ["staging", "production"],
                    "description": "Target environment"
                }
            },
            "required": ["environment"]
        },
        execute=deploy_execute
    ))
```

### Example 2: Code Statistics Command

```python
# ~/.agenix/extensions/code_stats.py
import os
from pathlib import Path
from agenix.extensions import CommandDefinition, EventType

async def setup(agenix):
    # Track tool usage
    tool_usage = {}

    @agenix.on(EventType.TOOL_CALL)
    async def track_tool_usage(event, ctx):
        tool_name = event.tool_name
        tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

    async def stats_handler(ctx, args):
        # Count files
        file_count = sum(1 for _ in Path(ctx.cwd).rglob("*.py"))

        # Show statistics
        ctx.notify(f"Python files: {file_count}", "info")
        ctx.notify(f"Messages: {len(ctx.messages)}", "info")

        if tool_usage:
            ctx.notify("Tool usage:", "info")
            for tool, count in sorted(tool_usage.items()):
                ctx.notify(f"  {tool}: {count} calls", "info")

    agenix.register_command(CommandDefinition(
        name="stats",
        description="Show project and session statistics",
        handler=stats_handler
    ))
```

### Example 3: Git Auto-commit

```python
# .agenix/extensions/git_autocommit.py
import subprocess
from agenix.extensions import EventType

async def setup(agenix):
    @agenix.on(EventType.TOOL_RESULT)
    async def auto_commit(event, ctx):
        # Auto-commit after file writes
        if event.tool_name == "write" and not event.is_error:
            # Check if in git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=ctx.cwd,
                capture_output=True
            )

            if result.returncode == 0:
                # Stage and commit
                subprocess.run(["git", "add", "-A"], cwd=ctx.cwd)
                subprocess.run(
                    ["git", "commit", "-m", "Auto-commit by agenix"],
                    cwd=ctx.cwd,
                    capture_output=True
                )
                ctx.notify("Changes auto-committed to git", "info")
```

### Example 4: SDK with Custom Extension

```python
# my_app.py
import asyncio
from agenix import create_session
from agenix.extensions import ToolDefinition

# Define a custom tool inline
async def custom_tool_execute(params, ctx):
    return f"Custom processing: {params['input']}"

async def main():
    # Create session with extensions
    session = await create_session(
        api_key="your-key",
        model="gpt-4o"
    )

    # The session automatically loads extensions from:
    # - ~/.agenix/extensions/
    # - .agenix/extensions/

    # Use the session
    response = await session.prompt(
        "Use the custom tool to process 'hello world'"
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Best Practices

1. **Error Handling**: Always handle errors in tool execution and event handlers
2. **Async**: Use `async def` for all handlers and tool execute functions
3. **Documentation**: Add docstrings to your tools and commands
4. **Namespacing**: Use descriptive, unique names for tools to avoid conflicts
5. **Testing**: Test your extensions before deploying

---

## Troubleshooting

### Extension Not Loading

1. Check the file is in the correct location (`~/.agenix/extensions/` or `.agenix/extensions/`)
2. Ensure the file has a `setup(agenix)` function
3. Check for syntax errors in the extension code
4. Look for error messages in the console output

### Tool Not Being Called

1. Verify the tool name and description are clear
2. Check the parameters schema is correct
3. Ensure the tool is actually registered (check for errors during setup)
4. Try explicitly asking the LLM to use your tool by name

---

For more examples, see the `examples/` directory in the agenix repository.
