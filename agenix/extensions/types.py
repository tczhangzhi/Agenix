"""Extension system types and interfaces.

Extensions are Python modules that can:
- Subscribe to agent lifecycle events
- Register custom LLM-callable tools
- Register custom commands
- Access agent context and UI primitives
"""

from dataclasses import dataclass
from enum import Enum
from typing import (TYPE_CHECKING, Any, Awaitable, Callable, Dict, List,
                    Optional, Protocol, TypeVar, Union)

if TYPE_CHECKING:
    from ..core.agent import Agent
    from ..tools.base import Tool


# ============================================================================
# Events
# ============================================================================

class EventType(str, Enum):
    """Agent lifecycle event types."""
    # Session events
    SESSION_START = "session_start"
    SESSION_END = "session_end"

    # Agent events
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    TURN_START = "turn_start"
    TURN_END = "turn_end"

    # Tool events
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"

    # Input event
    USER_INPUT = "user_input"


@dataclass
class Event:
    """Base event class."""
    type: EventType
    data: Dict[str, Any]


@dataclass
class SessionStartEvent(Event):
    """Fired when session starts."""

    def __init__(self):
        super().__init__(EventType.SESSION_START, {})


@dataclass
class SessionEndEvent(Event):
    """Fired when session ends."""

    def __init__(self):
        super().__init__(EventType.SESSION_END, {})


@dataclass
class AgentStartEvent(Event):
    """Fired when agent loop starts."""

    def __init__(self, prompt: str):
        super().__init__(EventType.AGENT_START, {"prompt": prompt})

    @property
    def prompt(self) -> str:
        return self.data["prompt"]


@dataclass
class AgentEndEvent(Event):
    """Fired when agent loop ends."""

    def __init__(self, messages: List[Any]):
        super().__init__(EventType.AGENT_END, {"messages": messages})

    @property
    def messages(self) -> List[Any]:
        return self.data["messages"]


@dataclass
class TurnStartEvent(Event):
    """Fired at the start of each turn."""

    def __init__(self, turn_index: int):
        super().__init__(EventType.TURN_START, {"turn_index": turn_index})

    @property
    def turn_index(self) -> int:
        return self.data["turn_index"]


@dataclass
class TurnEndEvent(Event):
    """Fired at the end of each turn."""

    def __init__(self, turn_index: int, message: Any):
        super().__init__(EventType.TURN_END, {
            "turn_index": turn_index,
            "message": message
        })

    @property
    def turn_index(self) -> int:
        return self.data["turn_index"]

    @property
    def message(self) -> Any:
        return self.data["message"]


@dataclass
class ToolCallEvent(Event):
    """Fired before a tool executes."""

    def __init__(self, tool_name: str, args: Dict[str, Any]):
        super().__init__(EventType.TOOL_CALL, {
            "tool_name": tool_name,
            "args": args
        })

    @property
    def tool_name(self) -> str:
        return self.data["tool_name"]

    @property
    def args(self) -> Dict[str, Any]:
        return self.data["args"]


@dataclass
class ToolResultEvent(Event):
    """Fired after a tool executes."""

    def __init__(self, tool_name: str, result: Any, is_error: bool):
        super().__init__(EventType.TOOL_RESULT, {
            "tool_name": tool_name,
            "result": result,
            "is_error": is_error
        })

    @property
    def tool_name(self) -> str:
        return self.data["tool_name"]

    @property
    def result(self) -> Any:
        return self.data["result"]

    @property
    def is_error(self) -> bool:
        return self.data["is_error"]


@dataclass
class UserInputEvent(Event):
    """Fired when user provides input."""

    def __init__(self, text: str):
        super().__init__(EventType.USER_INPUT, {"text": text})

    @property
    def text(self) -> str:
        return self.data["text"]


# ============================================================================
# Extension Context
# ============================================================================

class ExtensionContext:
    """Context passed to extension event handlers.

    Provides access to agent state and operations.
    """

    def __init__(
        self,
        agent: 'Agent',
        cwd: str,
        tools: List['Tool']
    ):
        self.agent = agent
        self.cwd = cwd
        self.tools = tools

    @property
    def messages(self) -> List[Any]:
        """Get current conversation messages."""
        return self.agent.messages

    def notify(self, message: str, type: str = "info") -> None:
        """Show a notification to the user."""
        # Simple implementation - print to console
        prefix = {
            "info": "ℹ️ ",
            "warning": "⚠️ ",
            "error": "❌ "
        }.get(type, "")
        print(f"{prefix}{message}")


# ============================================================================
# Tool Definition
# ============================================================================

@dataclass
class ToolDefinition:
    """Definition for a custom tool."""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema for parameters
    # async function(params, ctx) -> str
    execute: Callable[..., Awaitable[str]]


# ============================================================================
# Command Definition
# ============================================================================

@dataclass
class CommandDefinition:
    """Definition for a custom command."""
    name: str
    description: str
    # async function(ctx, args) -> None
    handler: Callable[[ExtensionContext, str], Awaitable[None]]


# ============================================================================
# Event Handler Types
# ============================================================================

EventHandler = Callable[[Event, ExtensionContext], Awaitable[None]]


# ============================================================================
# Extension API
# ============================================================================

class ExtensionAPI(Protocol):
    """API provided to extensions during setup.

    Extensions use this to register tools, commands, and event handlers.
    """

    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a custom tool that the LLM can call."""
        ...

    def register_command(self, command: CommandDefinition) -> None:
        """Register a custom command."""
        ...

    def on(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe to an event."""
        ...

    def notify(self, message: str, type: str = "info") -> None:
        """Show a notification."""
        ...


# ============================================================================
# Extension Factory
# ============================================================================

ExtensionSetup = Callable[[ExtensionAPI], Awaitable[None]]


# ============================================================================
# Loaded Extension
# ============================================================================

@dataclass
class LoadedExtension:
    """A loaded extension with its registered items."""
    path: str
    name: str
    tools: Dict[str, ToolDefinition]
    commands: Dict[str, CommandDefinition]
    handlers: Dict[EventType, List[EventHandler]]
