"""Extensions package - Tool registry and event types."""

from .tool_registry import ToolRegistry, ToolConfig
from .types import (
    EventType,
    Event,
    SessionStartEvent,
    SessionEndEvent,
    AgentStartEvent,
    AgentEndEvent,
    TurnStartEvent,
    TurnEndEvent,
    ToolCallEvent,
    ToolResultEvent,
    UserInputEvent,
    ExtensionContext,
    ToolDefinition,
    CommandDefinition,
    EventHandler,
    ExtensionAPI,
    ExtensionSetup,
    LoadedExtension,
)
from .loader import (
    ExtensionLoaderAPI,
    discover_extensions,
    load_extension,
    discover_and_load_extensions,
)
from .runner import ExtensionRunner

__all__ = [
    # Tool Registry
    "ToolRegistry",
    "ToolConfig",
    # Types
    "EventType",
    "Event",
    "SessionStartEvent",
    "SessionEndEvent",
    "AgentStartEvent",
    "AgentEndEvent",
    "TurnStartEvent",
    "TurnEndEvent",
    "ToolCallEvent",
    "ToolResultEvent",
    "UserInputEvent",
    "ExtensionContext",
    "ToolDefinition",
    "CommandDefinition",
    "EventHandler",
    "ExtensionAPI",
    "ExtensionSetup",
    "LoadedExtension",
    # Loader
    "ExtensionLoaderAPI",
    "discover_extensions",
    "load_extension",
    "discover_and_load_extensions",
    # Runner
    "ExtensionRunner",
]
