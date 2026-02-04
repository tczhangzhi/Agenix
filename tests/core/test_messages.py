"""Test suite for core.messages module.

This module contains unit tests for message types and event classes.
"""

from datetime import datetime

import pytest

from agenix.core.messages import (AgentEndEvent, AgentStartEvent,
                                  AssistantMessage, ImageContent,
                                  MessageStartEvent, SystemMessage,
                                  TextContent, ToolCall,
                                  ToolExecutionStartEvent, ToolResultMessage,
                                  TurnStartEvent, Usage, UserMessage)


class TestUserMessage:
    """Test cases for UserMessage class."""

    def test_create_user_message(self):
        """Test creating a basic user message."""
        msg = UserMessage(content="Hello")

        assert msg.role == "user"
        assert msg.content == "Hello"
        assert isinstance(msg.timestamp, float)

    def test_user_message_with_content_list(self):
        """Test creating user message with mixed content."""
        text = TextContent(text="Hello")
        image = ImageContent(source={"type": "base64", "data": "..."})

        msg = UserMessage(content=[text, image])

        assert msg.role == "user"
        assert len(msg.content) == 2
        assert isinstance(msg.content[0], TextContent)
        assert isinstance(msg.content[1], ImageContent)


class TestAssistantMessage:
    """Test cases for AssistantMessage class."""

    def test_create_assistant_message(self):
        """Test creating a basic assistant message."""
        msg = AssistantMessage(
            content="Response",
            model="gpt-4o"
        )

        assert msg.role == "assistant"
        assert msg.content == "Response"
        assert msg.model == "gpt-4o"
        assert msg.tool_calls == []

    def test_assistant_message_with_tool_calls(self):
        """Test creating assistant message with tool calls."""
        tool_call = ToolCall(
            id="call_123",
            name="bash",
            arguments={"command": "ls"}
        )

        msg = AssistantMessage(
            content=[TextContent(text="Running command...")],
            tool_calls=[tool_call],
            model="gpt-4o"
        )

        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0].name == "bash"
        assert msg.tool_calls[0].arguments["command"] == "ls"

    def test_assistant_message_with_usage(self):
        """Test creating assistant message with usage stats."""
        usage = Usage(
            input_tokens=100,
            output_tokens=50,
            total_cost=0.005
        )

        msg = AssistantMessage(
            content="Response",
            model="gpt-4o",
            usage=usage
        )

        assert msg.usage.input_tokens == 100
        assert msg.usage.output_tokens == 50
        assert msg.usage.total_cost == 0.005


class TestToolResultMessage:
    """Test cases for ToolResultMessage class."""

    def test_create_tool_result_message(self):
        """Test creating a tool result message."""
        msg = ToolResultMessage(
            tool_call_id="call_123",
            name="bash",
            content="output here"
        )

        assert msg.role == "tool"
        assert msg.tool_call_id == "call_123"
        assert msg.name == "bash"
        assert msg.content == "output here"
        assert msg.is_error is False

    def test_create_tool_error_message(self):
        """Test creating a tool error message."""
        msg = ToolResultMessage(
            tool_call_id="call_123",
            name="bash",
            content="Error: command not found",
            is_error=True
        )

        assert msg.is_error is True


class TestTextContent:
    """Test cases for TextContent class."""

    def test_create_text_content(self):
        """Test creating text content."""
        content = TextContent(text="Hello world")

        assert content.type == "text"
        assert content.text == "Hello world"


class TestImageContent:
    """Test cases for ImageContent class."""

    def test_create_image_content(self):
        """Test creating image content."""
        source = {
            "type": "base64",
            "media_type": "image/png",
            "data": "iVBORw0KGgoAAAANS..."
        }

        content = ImageContent(source=source)

        assert content.type == "image"
        assert content.source["type"] == "base64"
        assert content.source["media_type"] == "image/png"


class TestToolCall:
    """Test cases for ToolCall class."""

    def test_create_tool_call(self):
        """Test creating a tool call."""
        tool_call = ToolCall(
            id="call_abc123",
            name="read",
            arguments={"file_path": "test.py"}
        )

        assert tool_call.id == "call_abc123"
        assert tool_call.name == "read"
        assert tool_call.arguments["file_path"] == "test.py"


class TestUsage:
    """Test cases for Usage class."""

    def test_create_usage(self):
        """Test creating usage stats."""
        usage = Usage(
            input_tokens=100,
            output_tokens=50,
            cache_read_tokens=20,
            cache_write_tokens=10,
            total_cost=0.005
        )

        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.cache_read_tokens == 20
        assert usage.cache_write_tokens == 10
        assert usage.total_cost == 0.005


class TestEvents:
    """Test cases for event classes."""

    def test_agent_start_event(self):
        """Test creating agent start event."""
        event = AgentStartEvent()

        assert event.type == "agent_start"
        assert isinstance(event.timestamp, float)

    def test_agent_end_event(self):
        """Test creating agent end event."""
        msg = UserMessage(content="Hello")
        event = AgentEndEvent(messages=[msg])

        assert event.type == "agent_end"
        assert len(event.messages) == 1

    def test_turn_start_event(self):
        """Test creating turn start event."""
        event = TurnStartEvent()

        assert event.type == "turn_start"

    def test_message_start_event(self):
        """Test creating message start event."""
        msg = AssistantMessage(content="Test", model="gpt-4o")
        event = MessageStartEvent(message=msg)

        assert event.type == "message_start"
        assert event.message.content == "Test"

    def test_tool_execution_start_event(self):
        """Test creating tool execution start event."""
        event = ToolExecutionStartEvent(
            tool_call_id="call_123",
            tool_name="bash",
            args={"command": "ls"}
        )

        assert event.type == "tool_execution_start"
        assert event.tool_name == "bash"
        assert event.args["command"] == "ls"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
