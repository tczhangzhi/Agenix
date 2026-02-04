"""Core package initialization."""

from .agent import Agent, AgentConfig
from .llm import LLMProvider, LiteLLMProvider, StreamEvent, get_provider
from .messages import (
    Message,
    UserMessage,
    AssistantMessage,
    ToolResultMessage,
    SystemMessage,
    ToolCall,
    Usage,
    TextContent,
    ImageContent,
    Event,
    AgentStartEvent,
    AgentEndEvent,
    TurnStartEvent,
    TurnEndEvent,
    MessageStartEvent,
    MessageUpdateEvent,
    MessageEndEvent,
    ToolExecutionStartEvent,
    ToolExecutionUpdateEvent,
    ToolExecutionEndEvent,
)
from .session import SessionManager
from .settings import Settings, get_default_model, ensure_config_dir

__all__ = [
    # Agent
    "Agent",
    "AgentConfig",
    # LLM
    "LLMProvider",
    "LiteLLMProvider",
    "StreamEvent",
    "get_provider",
    # Messages
    "Message",
    "UserMessage",
    "AssistantMessage",
    "ToolResultMessage",
    "SystemMessage",
    "ToolCall",
    "Usage",
    "TextContent",
    "ImageContent",
    # Events
    "Event",
    "AgentStartEvent",
    "AgentEndEvent",
    "TurnStartEvent",
    "TurnEndEvent",
    "MessageStartEvent",
    "MessageUpdateEvent",
    "MessageEndEvent",
    "ToolExecutionStartEvent",
    "ToolExecutionUpdateEvent",
    "ToolExecutionEndEvent",
    # Session
    "SessionManager",
    # Settings
    "Settings",
    "get_default_model",
    "ensure_config_dir",
]
