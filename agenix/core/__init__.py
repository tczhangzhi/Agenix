"""Core package initialization."""

from .agent import Agent, AgentConfig
from .llm import LLMProvider, OpenAIProvider, AnthropicProvider, StreamEvent
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

__all__ = [
    # Agent
    "Agent",
    "AgentConfig",
    # LLM
    "LLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "StreamEvent",
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
]
