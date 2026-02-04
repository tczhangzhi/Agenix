"""Agenix - A simple and elegant agent framework."""

__version__ = "0.2.0"

from .core import (
    Agent,
    AgentConfig,
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    SessionManager,
    # Messages
    Message,
    UserMessage,
    AssistantMessage,
    ToolResultMessage,
    TextContent,
    ImageContent,
    ToolCall,
    Usage,
    # Events
    Event,
)

from .extensions import (
    # Agent Registry
    AgentRegistry,
    AgentConfig as RegistryAgentConfig,
    # Tool Registry
    ToolRegistry,
    ToolConfig,
    # Permission
    PermissionManager,
    PermissionRuleset,
    Rule,
    PermissionDeniedError,
)

from .tools import (
    Tool,
    ToolResult,
    ReadTool,
    WriteTool,
    EditTool,
    BashTool,
    GrepTool,
    GlobTool,
    SkillTool,
    TaskTool,
)

__all__ = [
    # Core
    "Agent",
    "AgentConfig",
    "LLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "SessionManager",
    # Messages
    "Message",
    "UserMessage",
    "AssistantMessage",
    "ToolResultMessage",
    "TextContent",
    "ImageContent",
    "ToolCall",
    "Usage",
    "Event",
    # Extensions - Registry
    "AgentRegistry",
    "RegistryAgentConfig",
    "ToolRegistry",
    "ToolConfig",
    # Extensions - Permission
    "PermissionManager",
    "PermissionRuleset",
    "Rule",
    "PermissionDeniedError",
    # Tools
    "Tool",
    "ToolResult",
    "ReadTool",
    "WriteTool",
    "EditTool",
    "BashTool",
    "GrepTool",
    "GlobTool",
    "SkillTool",
    "TaskTool",
]
