"""Agenix - A lightweight AI coding agent.

A minimal Python implementation inspired by pi-mono, supporting OpenAI and
Anthropic LLMs with file operations, shell execution, Agent Skills, and Extensions.

## Programmatic Usage (SDK)

```python
import asyncio
from agenix import create_session

async def main():
    session = await create_session(
        api_key="your-key",
        model="gpt-4o"
    )
    response = await session.prompt("What files are in the current directory?")
    print(response)

asyncio.run(main())
```

## Extension System

Extensions can be placed in:
- Global: `~/.agenix/extensions/`
- Project: `.agenix/extensions/`

Example extension:
```python
# ~/.agenix/extensions/my_tool.py
async def setup(agenix):
    from agenix.extensions import ToolDefinition, EventType

    async def my_execute(params, ctx):
        return f"Result: {params}"

    agenix.register_tool(ToolDefinition(
        name="my_tool",
        description="My custom tool",
        parameters={"type": "object"},
        execute=my_execute
    ))
```
"""

__version__ = "0.0.1"
__author__ = "ZHANG Zhi"
__email__ = "tczhangzhi@gmail.com"
__license__ = "MIT"

# Core
from .core.agent import Agent, AgentConfig
from .core.llm import get_provider
from .core.session import SessionManager
from .core.skills import Skill, SkillManager
from .core.messages import (
    Message,
    UserMessage,
    AssistantMessage,
    ToolResultMessage,
    TextContent,
    ImageContent,
    ToolCall,
)

# Tools
from .tools.read import ReadTool
from .tools.write import WriteTool
from .tools.edit import EditTool
from .tools.bash import BashTool
from .tools.grep import GrepTool

# SDK
from .sdk import create_session, AgentSession

# Extensions (for extension authors)
from . import extensions

__all__ = [
    # SDK (main API for programmatic usage)
    "create_session",
    "AgentSession",

    # Core
    "Agent",
    "AgentConfig",
    "get_provider",
    "SessionManager",
    "Skill",
    "SkillManager",

    # Messages
    "Message",
    "UserMessage",
    "AssistantMessage",
    "ToolResultMessage",
    "TextContent",
    "ImageContent",
    "ToolCall",

    # Tools
    "ReadTool",
    "WriteTool",
    "EditTool",
    "BashTool",
    "GrepTool",

    # Extensions
    "extensions",
]
