"""Agenix - A simple and elegant agent framework."""

__version__ = "0.2.0"

from .core import (
    Agent,
    AgentConfig,
    LLMProvider,
    LiteLLMProvider,
    get_provider,
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
    # Tool Registry
    ToolRegistry,
    ToolConfig,
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
    "LiteLLMProvider",
    "get_provider",
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
    "ToolRegistry",
    "ToolConfig",
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
