"""Tests for LLM providers - OpenAI and Anthropic."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agenix.core.llm import (PROVIDERS, AnthropicProvider, LLMProvider,
                              OpenAIProvider, StreamEvent, get_provider)
from agenix.core.messages import (AssistantMessage, ImageContent, TextContent,
                                   ToolCall, ToolResultMessage, UserMessage)


class TestStreamEvent:
    """Test StreamEvent dataclass."""

    def test_create_text_delta_event(self):
        """Test creating text delta event."""
        event = StreamEvent(type="text_delta", delta="Hello")

        assert event.type == "text_delta"
        assert event.delta == "Hello"
        assert event.tool_call is None

    def test_create_tool_call_event(self):
        """Test creating tool call event."""
        tool_call = ToolCall(id="call_123", name="read", arguments={"file": "test.py"})
        event = StreamEvent(type="tool_call", tool_call=tool_call)

        assert event.type == "tool_call"
        assert event.tool_call == tool_call

    def test_create_finish_event(self):
        """Test creating finish event."""
        event = StreamEvent(type="finish", finish_reason="stop")

        assert event.type == "finish"
        assert event.finish_reason == "stop"


class TestLLMProviderBase:
    """Test abstract LLMProvider base class."""

    def test_provider_initialization(self):
        """Test provider initialization with API key."""
        # Can't instantiate abstract class directly
        # Test via concrete implementation
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider()
            assert provider.api_key == "test-key"

    def test_messages_to_dict_user_message(self):
        """Test converting user message to dict."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider()

            messages = [UserMessage(content="Hello")]
            result = provider._messages_to_dict(messages)

            assert len(result) == 1
            assert result[0]["role"] == "user"
            assert result[0]["content"] == "Hello"

    def test_messages_to_dict_assistant_message(self):
        """Test converting assistant message to dict."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider()

            messages = [AssistantMessage(content=[TextContent(text="Hi there")])]
            result = provider._messages_to_dict(messages)

            assert len(result) == 1
            assert result[0]["role"] == "assistant"
            assert result[0]["content"] == "Hi there"

    def test_messages_to_dict_with_tool_calls(self):
        """Test converting assistant message with tool calls."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider()

            tool_call = ToolCall(id="call_1", name="read", arguments={"file": "test.py"})
            messages = [AssistantMessage(
                content=[TextContent(text="Let me read that")],
                tool_calls=[tool_call]
            )]
            result = provider._messages_to_dict(messages)

            assert len(result) == 1
            assert "tool_calls" in result[0]
            assert len(result[0]["tool_calls"]) == 1
            assert result[0]["tool_calls"][0]["function"]["name"] == "read"

    def test_messages_to_dict_tool_result(self):
        """Test converting tool result message."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider()

            messages = [ToolResultMessage(
                tool_call_id="call_1",
                content="File content here",
                is_error=False
            )]
            result = provider._messages_to_dict(messages)

            assert len(result) == 1
            assert result[0]["role"] == "tool"
            assert result[0]["tool_call_id"] == "call_1"
            assert "File content" in result[0]["content"]


class TestOpenAIProvider:
    """Test OpenAI provider."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        provider = OpenAIProvider(api_key="test-key")

        assert provider.api_key == "test-key"
        # Base URL may come from environment or default
        assert provider.base_url is not None

    def test_init_with_env_var(self):
        """Test initialization from environment variable."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'env-key'}):
            provider = OpenAIProvider()
            assert provider.api_key == "env-key"

    def test_init_without_api_key_raises(self):
        """Test that missing API key raises error."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                OpenAIProvider()

    def test_custom_base_url(self):
        """Test custom base URL."""
        provider = OpenAIProvider(api_key="test-key", base_url="https://custom.api")

        assert provider.base_url == "https://custom.api"

    def test_convert_tool(self):
        """Test tool conversion to OpenAI format."""
        provider = OpenAIProvider(api_key="test-key")

        tool = {
            "name": "read",
            "description": "Read a file",
            "parameters": {"type": "object", "properties": {}}
        }

        result = provider._convert_tool(tool)

        assert result["type"] == "function"
        assert result["function"]["name"] == "read"
        assert result["function"]["description"] == "Read a file"


class TestAnthropicProvider:
    """Test Anthropic provider."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        provider = AnthropicProvider(api_key="test-key")

        assert provider.api_key == "test-key"

    def test_init_with_env_var(self):
        """Test initialization from environment variable."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'env-key'}):
            provider = AnthropicProvider()
            assert provider.api_key == "env-key"

    def test_init_without_api_key_raises(self):
        """Test that missing API key raises error."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                AnthropicProvider()

    def test_convert_tool(self):
        """Test tool conversion to Anthropic format."""
        provider = AnthropicProvider(api_key="test-key")

        tool = {
            "name": "read",
            "description": "Read a file",
            "parameters": {"type": "object", "properties": {}}
        }

        result = provider._convert_tool(tool)

        assert result["name"] == "read"
        assert result["description"] == "Read a file"
        assert "input_schema" in result

    def test_anthropic_messages_conversion(self):
        """Test message conversion to Anthropic format."""
        provider = AnthropicProvider(api_key="test-key")

        messages = [
            UserMessage(content="Hello"),
            AssistantMessage(content=[TextContent(text="Hi")])
        ]

        result = provider._anthropic_messages(messages)

        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "assistant"


class TestProviderRegistry:
    """Test provider registry."""

    def test_registry_contains_providers(self):
        """Test that registry contains expected providers."""
        assert "openai" in PROVIDERS
        assert "anthropic" in PROVIDERS
        assert PROVIDERS["openai"] == OpenAIProvider
        assert PROVIDERS["anthropic"] == AnthropicProvider

    def test_get_provider_openai(self):
        """Test getting OpenAI provider."""
        provider = get_provider("openai", api_key="test-key")

        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == "test-key"

    def test_get_provider_anthropic(self):
        """Test getting Anthropic provider."""
        provider = get_provider("anthropic", api_key="test-key")

        assert isinstance(provider, AnthropicProvider)
        assert provider.api_key == "test-key"

    def test_get_provider_unknown_raises(self):
        """Test that unknown provider raises error."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("unknown-provider")


class TestContentFormatting:
    """Test content formatting methods."""

    def test_format_text_only_content(self):
        """Test formatting text-only content."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider()

            content = [TextContent(text="Hello"), TextContent(text="World")]
            result = provider._format_content(content)

            assert isinstance(result, str)
            assert "Hello" in result
            assert "World" in result

    def test_format_mixed_content_with_image(self):
        """Test formatting mixed content with images."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider()

            content = [
                TextContent(text="Look at this:"),
                ImageContent(source={
                    "type": "base64",
                    "media_type": "image/png",
                    "data": "abc123"
                })
            ]
            result = provider._format_content(content)

            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["type"] == "text"
            assert result[1]["type"] == "image_url"


# Note: Full integration tests with actual API calls would require
# mocking the openai and anthropic libraries more extensively.
# The tests above cover the core functionality and error handling.

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
