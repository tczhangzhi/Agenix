"""Tests for LiteLLM provider."""

import pytest
from unittest.mock import MagicMock, patch

from agenix.core.llm import LiteLLMProvider, StreamEvent, get_provider
from agenix.core.messages import TextContent, ToolCall


class TestStreamEvent:
    """Test StreamEvent dataclass."""

    def test_create_text_delta_event(self):
        """Test creating text delta event."""
        event = StreamEvent(type="text_delta", delta="Hello")

        assert event.type == "text_delta"
        assert event.delta == "Hello"
        assert event.tool_call is None
        assert event.finish_reason is None

    def test_create_tool_call_event(self):
        """Test creating tool call event."""
        tool_call = ToolCall(id="call_123", name="read", arguments={"file": "test.py"})
        event = StreamEvent(type="tool_call", tool_call=tool_call)

        assert event.type == "tool_call"
        assert event.tool_call == tool_call
        assert event.delta == ""

    def test_create_finish_event(self):
        """Test creating finish event."""
        event = StreamEvent(type="finish", finish_reason="stop")

        assert event.type == "finish"
        assert event.finish_reason == "stop"

    def test_create_reasoning_delta_event(self):
        """Test creating reasoning delta event."""
        event = StreamEvent(
            type="reasoning_delta",
            delta="Let me think...",
            reasoning_block_id="reasoning_0"
        )

        assert event.type == "reasoning_delta"
        assert event.delta == "Let me think..."
        assert event.reasoning_block_id == "reasoning_0"


class TestLiteLLMProvider:
    """Test LiteLLMProvider."""

    def test_provider_initialization(self):
        """Test that provider can be initialized."""
        try:
            provider = LiteLLMProvider(
                api_key="test-key",
                model="gpt-4o"
            )
            assert provider.api_key == "test-key"
            assert provider.default_model == "gpt-4o"
        except ImportError:
            pytest.skip("litellm not installed")

    def test_openrouter_detection(self):
        """Test that OpenRouter is detected from API key."""
        try:
            provider = LiteLLMProvider(
                api_key="sk-or-test-key",
                model="anthropic/claude-sonnet-4-5"
            )
            assert provider.is_openrouter is True
        except ImportError:
            pytest.skip("litellm not installed")

    def test_custom_endpoint_detection(self):
        """Test that custom endpoints are detected."""
        try:
            provider = LiteLLMProvider(
                api_key="test-key",
                base_url="http://localhost:8000/v1",
                model="llama-3"
            )
            assert provider.is_custom_endpoint is True
        except ImportError:
            pytest.skip("litellm not installed")

    def test_model_name_normalization(self):
        """Test model name normalization."""
        try:
            # OpenRouter
            provider = LiteLLMProvider(api_key="sk-or-test", model="test")
            assert provider._normalize_model_name("claude-sonnet-4-5") == "openrouter/claude-sonnet-4-5"

            # Gemini
            provider = LiteLLMProvider(api_key="test", model="gpt-4o")
            assert provider._normalize_model_name("gemini-pro") == "gemini/gemini-pro"

            # Claude
            assert provider._normalize_model_name("claude-sonnet-4-5") == "anthropic/claude-sonnet-4-5"

            # Already prefixed
            assert provider._normalize_model_name("anthropic/claude-sonnet-4-5") == "anthropic/claude-sonnet-4-5"
        except ImportError:
            pytest.skip("litellm not installed")


class TestGetProvider:
    """Test get_provider function."""

    def test_get_provider_returns_litellm(self):
        """Test that get_provider returns LiteLLMProvider."""
        try:
            provider = get_provider(api_key="test-key", model="gpt-4o")
            assert isinstance(provider, LiteLLMProvider)
        except ImportError:
            pytest.skip("litellm not installed")

    def test_get_provider_with_reasoning_effort(self):
        """Test that reasoning effort is passed through."""
        try:
            provider = get_provider(
                api_key="test-key",
                model="o1-preview",
                reasoning_effort="high"
            )
            assert provider.reasoning_effort == "high"
        except ImportError:
            pytest.skip("litellm not installed")
