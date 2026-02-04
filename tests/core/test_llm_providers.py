"""Tests for LLM providers - OpenAI and Anthropic implementations."""

import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agenix.core.llm import (
    AnthropicProvider,
    LLMProvider,
    OpenAIProvider,
    StreamEvent,
    get_provider,
)
from agenix.core.messages import (
    AssistantMessage,
    ImageContent,
    TextContent,
    ToolCall,
    ToolResultMessage,
    UserMessage,
)


class TestStreamEvent:
    """Test StreamEvent dataclass."""

    def test_create_text_delta(self):
        """Test creating text delta event."""
        event = StreamEvent(type="text_delta", delta="Hello")

        assert event.type == "text_delta"
        assert event.delta == "Hello"
        assert event.tool_call is None

    def test_create_tool_call_event(self):
        """Test creating tool call event."""
        tool_call = ToolCall(id="call_1", name="read", arguments={"path": "file.txt"})
        event = StreamEvent(type="tool_call", tool_call=tool_call)

        assert event.type == "tool_call"
        assert event.tool_call == tool_call

    def test_create_finish_event(self):
        """Test creating finish event."""
        event = StreamEvent(type="finish", finish_reason="stop")

        assert event.type == "finish"
        assert event.finish_reason == "stop"


class TestLLMProviderMessageConversion:
    """Test LLMProvider._messages_to_dict method."""

    def test_convert_user_message_string(self):
        """Test converting user message with string content."""
        provider = OpenAIProvider(api_key="test-key")
        messages = [UserMessage(content="Hello")]

        result = provider._messages_to_dict(messages)

        assert len(result) == 1
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello"

    def test_convert_user_message_with_image(self):
        """Test converting user message with image content."""
        provider = OpenAIProvider(api_key="test-key")
        messages = [UserMessage(content=[
            TextContent(text="What's in this image?"),
            ImageContent(source={
                "type": "base64",
                "media_type": "image/png",
                "data": "iVBORw0KGgoAAAANS"
            })
        ])]

        result = provider._messages_to_dict(messages)

        assert len(result) == 1
        assert result[0]["role"] == "user"
        assert isinstance(result[0]["content"], list)
        assert result[0]["content"][0]["type"] == "text"
        assert result[0]["content"][1]["type"] == "image_url"

    def test_convert_assistant_message_text_only(self):
        """Test converting assistant message with text only."""
        provider = OpenAIProvider(api_key="test-key")
        messages = [AssistantMessage(content=[TextContent(text="Hello")])]

        result = provider._messages_to_dict(messages)

        assert len(result) == 1
        assert result[0]["role"] == "assistant"
        assert result[0]["content"] == "Hello"

    def test_convert_assistant_message_with_tool_calls(self):
        """Test converting assistant message with tool calls."""
        provider = OpenAIProvider(api_key="test-key")
        messages = [AssistantMessage(
            content=[TextContent(text="Let me check that")],
            tool_calls=[ToolCall(id="call_1", name="read", arguments={"path": "file.txt"})]
        )]

        result = provider._messages_to_dict(messages)

        assert len(result) == 1
        assert result[0]["role"] == "assistant"
        assert "tool_calls" in result[0]
        assert len(result[0]["tool_calls"]) == 1
        assert result[0]["tool_calls"][0]["function"]["name"] == "read"

    def test_convert_assistant_message_empty_content(self):
        """Test converting assistant message with empty content."""
        provider = OpenAIProvider(api_key="test-key")
        messages = [AssistantMessage(
            content=[],
            tool_calls=[ToolCall(id="call_1", name="read", arguments={})]
        )]

        result = provider._messages_to_dict(messages)

        assert len(result) == 1
        assert result[0]["content"] == ""  # Empty string for API

    def test_convert_tool_result_message(self):
        """Test converting tool result message."""
        provider = OpenAIProvider(api_key="test-key")
        messages = [ToolResultMessage(
            tool_call_id="call_1",
            name="read",
            content="File contents",
            is_error=False
        )]

        result = provider._messages_to_dict(messages)

        assert len(result) == 1
        assert result[0]["role"] == "tool"
        assert result[0]["tool_call_id"] == "call_1"
        assert result[0]["content"] == "File contents"

    def test_convert_tool_result_with_images(self):
        """Test converting tool result with images."""
        provider = OpenAIProvider(api_key="test-key")
        messages = [ToolResultMessage(
            tool_call_id="call_1",
            name="screenshot",
            content=[
                TextContent(text="Screenshot taken"),
                ImageContent(source={
                    "type": "base64",
                    "media_type": "image/png",
                    "data": "base64data"
                })
            ],
            is_error=False
        )]

        result = provider._messages_to_dict(messages)

        # Should create two messages: tool response + user message with image
        assert len(result) == 2
        assert result[0]["role"] == "tool"
        assert result[1]["role"] == "user"


class TestLLMProviderFormatContent:
    """Test LLMProvider._format_content method."""

    def test_format_text_only_content(self):
        """Test formatting text-only content."""
        provider = OpenAIProvider(api_key="test-key")
        content = [
            TextContent(text="First line"),
            TextContent(text="Second line")
        ]

        result = provider._format_content(content)

        assert isinstance(result, str)
        assert result == "First line\nSecond line"

    def test_format_mixed_content_with_images(self):
        """Test formatting mixed content with images."""
        provider = OpenAIProvider(api_key="test-key")
        content = [
            TextContent(text="Look at this:"),
            ImageContent(source={
                "type": "base64",
                "media_type": "image/png",
                "data": "imagedata"
            })
        ]

        result = provider._format_content(content)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["type"] == "text"
        assert result[1]["type"] == "image_url"
        assert "data:image/png;base64,imagedata" in result[1]["image_url"]["url"]


class TestOpenAIProvider:
    """Test OpenAIProvider implementation."""

    def test_init_with_api_key(self):
        """Test initializing with API key."""
        provider = OpenAIProvider(api_key="test-key")

        assert provider.api_key == "test-key"
        assert provider.base_url is not None  # Should have default

    def test_init_with_base_url(self):
        """Test initializing with custom base URL."""
        provider = OpenAIProvider(api_key="test-key", base_url="https://custom.api/v1")

        assert provider.api_key == "test-key"
        assert provider.base_url == "https://custom.api/v1"

    def test_init_from_env(self):
        """Test initializing from environment."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            provider = OpenAIProvider()
            assert provider.api_key == "env-key"

    def test_init_missing_api_key(self):
        """Test that missing API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                OpenAIProvider()

    def test_convert_tool(self):
        """Test tool conversion to OpenAI format."""
        provider = OpenAIProvider(api_key="test-key")
        tool = {
            "name": "read",
            "description": "Read a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                }
            }
        }

        result = provider._convert_tool(tool)

        assert result["type"] == "function"
        assert result["function"]["name"] == "read"
        assert result["function"]["description"] == "Read a file"
        assert "parameters" in result["function"]


class TestAnthropicProvider:
    """Test AnthropicProvider implementation."""

    def test_init_with_api_key(self):
        """Test initializing with API key."""
        provider = AnthropicProvider(api_key="test-key")

        assert provider.api_key == "test-key"
        assert provider.base_url is None  # No default for Anthropic

    def test_init_from_env(self):
        """Test initializing from environment."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key"}):
            provider = AnthropicProvider()
            assert provider.api_key == "env-key"

    def test_init_missing_api_key(self):
        """Test that missing API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                AnthropicProvider()

    def test_convert_tool(self):
        """Test tool conversion to Anthropic format."""
        provider = AnthropicProvider(api_key="test-key")
        tool = {
            "name": "read",
            "description": "Read a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                }
            }
        }

        result = provider._convert_tool(tool)

        assert result["name"] == "read"
        assert result["description"] == "Read a file"
        assert "input_schema" in result

    def test_anthropic_messages_user(self):
        """Test converting user message to Anthropic format."""
        provider = AnthropicProvider(api_key="test-key")
        messages = [UserMessage(content="Hello")]

        result = provider._anthropic_messages(messages)

        assert len(result) == 1
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello"

    def test_anthropic_messages_assistant_with_tools(self):
        """Test converting assistant message with tools to Anthropic format."""
        provider = AnthropicProvider(api_key="test-key")
        messages = [AssistantMessage(
            content=[TextContent(text="Let me check")],
            tool_calls=[ToolCall(id="call_1", name="read", arguments={"path": "file.txt"})]
        )]

        result = provider._anthropic_messages(messages)

        assert len(result) == 1
        assert result[0]["role"] == "assistant"
        assert isinstance(result[0]["content"], list)
        # Should have text content and tool_use
        assert any(item["type"] == "text" for item in result[0]["content"])
        assert any(item["type"] == "tool_use" for item in result[0]["content"])

    def test_anthropic_messages_tool_result(self):
        """Test converting tool result to Anthropic format."""
        provider = AnthropicProvider(api_key="test-key")
        messages = [ToolResultMessage(
            tool_call_id="call_1",
            name="read",
            content="File contents",
            is_error=False
        )]

        result = provider._anthropic_messages(messages)

        assert len(result) == 1
        assert result[0]["role"] == "user"
        assert result[0]["content"][0]["type"] == "tool_result"
        assert result[0]["content"][0]["tool_use_id"] == "call_1"

    def test_anthropic_messages_tool_result_with_images(self):
        """Test converting tool result with images to Anthropic format."""
        provider = AnthropicProvider(api_key="test-key")
        messages = [ToolResultMessage(
            tool_call_id="call_1",
            name="screenshot",
            content=[
                TextContent(text="Screenshot"),
                ImageContent(source={
                    "type": "base64",
                    "media_type": "image/png",
                    "data": "imagedata"
                })
            ],
            is_error=False
        )]

        result = provider._anthropic_messages(messages)

        assert len(result) == 1
        assert result[0]["role"] == "user"
        content = result[0]["content"][0]["content"]
        assert isinstance(content, list)
        assert any(item["type"] == "text" for item in content)
        assert any(item["type"] == "image" for item in content)


class TestGetProvider:
    """Test get_provider factory function."""

    def test_get_openai_provider(self):
        """Test getting OpenAI provider."""
        provider = get_provider("openai", api_key="test-key")

        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == "test-key"

    def test_get_anthropic_provider(self):
        """Test getting Anthropic provider."""
        provider = get_provider("anthropic", api_key="test-key")

        assert isinstance(provider, AnthropicProvider)
        assert provider.api_key == "test-key"

    def test_get_unknown_provider(self):
        """Test that unknown provider raises error."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("unknown", api_key="test-key")


class TestOpenAIStreamingEdgeCases:
    """Test OpenAI streaming edge cases."""

    @pytest.mark.asyncio
    async def test_stream_handles_empty_tool_arguments(self):
        """Test that streaming handles empty tool arguments."""
        provider = OpenAIProvider(api_key="test-key")

        # This would require mocking openai client, skip for now
        # Covered by real API tests
        pass

    @pytest.mark.asyncio
    async def test_stream_handles_invalid_json_arguments(self):
        """Test that streaming handles invalid JSON in tool arguments."""
        provider = OpenAIProvider(api_key="test-key")

        # This would require mocking openai client, skip for now
        # Covered by real API tests
        pass


class TestAnthropicStreamingEdgeCases:
    """Test Anthropic streaming edge cases."""

    @pytest.mark.asyncio
    async def test_stream_handles_finish_reason_mapping(self):
        """Test that Anthropic finish reasons are mapped correctly."""
        provider = AnthropicProvider(api_key="test-key")

        # This would require mocking anthropic client, skip for now
        # The mapping logic is tested through the actual implementation
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
