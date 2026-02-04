"""Extension system for agenix.

Allows Python modules to extend agenix with:
- Custom tools
- Event handlers
- Commands

Example extension:

```python
# ~/.agenix/extensions/my_extension.py
async def setup(agenix):
    \"\"\"Extension setup function.\"\"\"

    # Register a custom tool
    from agenix.extensions import ToolDefinition

    async def my_tool_execute(params, ctx):
        # Tool implementation
        return f"Executed with: {params}"

    agenix.register_tool(ToolDefinition(
        name="my_tool",
        description="My custom tool",
        parameters={
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            }
        },
        execute=my_tool_execute
    ))

    # Register event handler
    from agenix.extensions import EventType

    @agenix.on(EventType.TOOL_CALL)
    async def on_tool_call(event, ctx):
        print(f"Tool called: {event.tool_name}")

    # Register a command
    from agenix.extensions import CommandDefinition

    async def stats_handler(ctx, args):
        print(f"Stats command executed with: {args}")

    agenix.register_command(CommandDefinition(
        name="stats",
        description="Show statistics",
        handler=stats_handler
    ))
```
"""

from .types import (
    # Events
    Event,
    EventType,
    SessionStartEvent,
    SessionEndEvent,
    AgentStartEvent,
    AgentEndEvent,
    TurnStartEvent,
    TurnEndEvent,
    ToolCallEvent,
    ToolResultEvent,
    UserInputEvent,

    # Context
    ExtensionContext,

    # Definitions
    ToolDefinition,
    CommandDefinition,

    # API
    ExtensionAPI,
    ExtensionSetup,

    # Loaded extension
    LoadedExtension
)

from .loader import (
    discover_and_load_extensions,
    load_extension
)

from .runner import ExtensionRunner

__all__ = [
    # Events
    "Event",
    "EventType",
    "SessionStartEvent",
    "SessionEndEvent",
    "AgentStartEvent",
    "AgentEndEvent",
    "TurnStartEvent",
    "TurnEndEvent",
    "ToolCallEvent",
    "ToolResultEvent",
    "UserInputEvent",

    # Context
    "ExtensionContext",

    # Definitions
    "ToolDefinition",
    "CommandDefinition",

    # API
    "ExtensionAPI",
    "ExtensionSetup",

    # Loaded
    "LoadedExtension",

    # Functions
    "discover_and_load_extensions",
    "load_extension",

    # Runner
    "ExtensionRunner",
]
