"""Programmatic SDK for using agenix as a library.

Example usage:

```python
import asyncio
from agenix import create_session

async def main():
    # Create a session
    session = await create_session(
        api_key="your-api-key",
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

if __name__ == "__main__":
    asyncio.run(main())
```
"""

from .extensions import (CommandDefinition, EventType, ExtensionAPI,
                         ExtensionSetup, ToolDefinition)
import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .core.agent import Agent, AgentConfig
from .core.messages import Message
from .extensions import (ExtensionContext, ExtensionRunner, SessionEndEvent,
                         SessionStartEvent, discover_and_load_extensions)
from .tools.bash import BashTool
from .tools.edit import EditTool
from .tools.grep import GrepTool
from .tools.read import ReadTool
from .tools.write import WriteTool


class AgentSession:
    """High-level agent session for programmatic usage.

    Wraps the low-level Agent class with a simpler API.
    """

    def __init__(
        self,
        agent: Agent,
        tools: List[Any],
        extension_runner: Optional[ExtensionRunner] = None,
        working_dir: str = "."
    ):
        self.agent = agent
        self.tools = tools
        self.extension_runner = extension_runner
        self.working_dir = working_dir
        self._started = False

    async def _ensure_started(self) -> None:
        """Ensure session has been started."""
        if not self._started:
            if self.extension_runner:
                await self.extension_runner.emit(SessionStartEvent())
            self._started = True

    async def prompt(self, message: str) -> str:
        """Send a prompt to the agent and return the response.

        Args:
            message: User message/prompt

        Returns:
            Agent's text response
        """
        await self._ensure_started()

        # Collect the response
        response_parts = []

        async for event in self.agent.prompt(message):
            # Collect text from message update events
            from .core.messages import MessageUpdateEvent
            if isinstance(event, MessageUpdateEvent):
                response_parts.append(event.delta)

        return "".join(response_parts)

    def get_messages(self) -> List[Message]:
        """Get conversation history.

        Returns:
            List of messages in the conversation
        """
        return self.agent.messages

    def clear_messages(self) -> None:
        """Clear conversation history."""
        self.agent.clear_messages()

    async def close(self) -> None:
        """Close the session and cleanup."""
        if self.extension_runner:
            await self.extension_runner.emit(SessionEndEvent())


async def create_session(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: str = "gpt-4o",
    system_prompt: Optional[str] = None,
    working_dir: str = ".",
    max_turns: int = 10,
    enable_extensions: bool = True
) -> AgentSession:
    """Create an agent session for programmatic usage.

    Args:
        api_key: API key for the LLM provider (or set OPENAI_API_KEY env var)
        base_url: Optional API base URL
        model: Model to use (default: gpt-4o)
        system_prompt: Optional custom system prompt
        working_dir: Working directory for file operations
        max_turns: Maximum conversation turns per prompt
        enable_extensions: Whether to load extensions

    Returns:
        AgentSession instance

    Example:
        >>> import asyncio
        >>> from agenix import create_session
        >>>
        >>> async def main():
        ...     session = await create_session(
        ...         api_key="your-key",
        ...         model="gpt-4o"
        ...     )
        ...     response = await session.prompt("Hello!")
        ...     print(response)
        ...
        >>> asyncio.run(main())
    """
    # Get API key
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "API key required. Set OPENAI_API_KEY environment variable "
            "or pass api_key parameter."
        )

    # Resolve working directory
    working_dir = os.path.abspath(working_dir)

    # Setup tools
    tools = [
        ReadTool(working_dir=working_dir),
        WriteTool(working_dir=working_dir),
        EditTool(working_dir=working_dir),
        BashTool(working_dir=working_dir),
        GrepTool(working_dir=working_dir),
    ]

    # Load extensions if enabled
    extension_runner = None
    if enable_extensions:
        extensions = await discover_and_load_extensions(cwd=working_dir)
        if extensions:
            # Create extension context
            # Note: We need an agent instance, so we'll create it first
            # and then set up extensions
            pass

    # Get default system prompt if not provided
    if not system_prompt:
        from .cli import get_default_system_prompt
        system_prompt = get_default_system_prompt(tools)

    # Create agent config
    config = AgentConfig(
        model=model,
        api_key=api_key,
        base_url=base_url,
        system_prompt=system_prompt,
        max_turns=max_turns
    )

    # Create agent
    agent = Agent(config=config, tools=tools)

    # Setup extension runner if extensions were loaded
    if enable_extensions:
        extensions = await discover_and_load_extensions(cwd=working_dir)
        if extensions:
            ext_context = ExtensionContext(
                agent=agent,
                cwd=working_dir,
                tools=tools
            )
            extension_runner = ExtensionRunner(extensions, ext_context)

    # Create session
    session = AgentSession(
        agent=agent,
        tools=tools,
        extension_runner=extension_runner,
        working_dir=working_dir
    )

    return session


# Re-export key types for convenience

__all__ = [
    # Main API
    "create_session",
    "AgentSession",

    # Extension types (for custom extensions)
    "ToolDefinition",
    "CommandDefinition",
    "ExtensionAPI",
    "ExtensionSetup",
    "EventType",
]
