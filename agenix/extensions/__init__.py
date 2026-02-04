"""Extensions package - Agent registry, tool registry, and permissions."""

from .agent_registry import AgentRegistry, AgentConfig
from .tool_registry import ToolRegistry, ToolConfig
from .permission import (
    PermissionManager,
    PermissionRuleset,
    Rule,
    PermissionDeniedError,
    Action,
)
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
    # Agent Registry
    "AgentRegistry",
    "AgentConfig",
    # Tool Registry
    "ToolRegistry",
    "ToolConfig",
    # Permission
    "PermissionManager",
    "PermissionRuleset",
    "Rule",
    "PermissionDeniedError",
    "Action",
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
