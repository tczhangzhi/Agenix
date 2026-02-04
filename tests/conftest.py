"""Test configuration for pytest.

This module configures pytest for the agenix test suite.
"""

import os
import sys
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
env_file = project_root / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def pytest_configure(config):
    """Configure pytest with custom markers.

    Args:
        config: Pytest configuration object
    """
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


# Import after path setup
from agenix.core.llm import LLMProvider, StreamEvent
from agenix.core.messages import AssistantMessage, TextContent, ToolCall, Usage


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        response_text: str = "Mock response",
        tool_calls: Optional[List[ToolCall]] = None,
    ):
        super().__init__(api_key=api_key, base_url=base_url)
        self.response_text = response_text
        self.tool_calls = tool_calls or []
        self.call_count = 0

    async def stream(
        self,
        model: str,
        messages: List,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
    ) -> AsyncIterator[StreamEvent]:
        """Mock stream implementation."""
        self.call_count += 1

        # Yield text
        if self.response_text:
            yield StreamEvent(type="text_delta", delta=self.response_text)

        # Yield tool calls
        for tc in self.tool_calls:
            yield StreamEvent(type="tool_call", tool_call=tc)

        # Yield finish
        yield StreamEvent(type="finish", finish_reason="stop")

    async def complete(
        self,
        model: str,
        messages: List,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
    ) -> AssistantMessage:
        """Mock complete implementation."""
        self.call_count += 1

        content = [TextContent(text=self.response_text)]

        return AssistantMessage(
            content=content,
            tool_calls=self.tool_calls,
            model=model,
            usage=Usage(input_tokens=10, output_tokens=20),
            stop_reason="stop",
        )


@pytest.fixture
def mock_provider():
    """Fixture providing a mock LLM provider."""
    return MockLLMProvider()


@pytest.fixture
def mock_provider_with_tool_call():
    """Fixture providing a mock LLM provider that makes tool calls."""
    tool_call = ToolCall(
        id="call_123",
        name="test_tool",
        arguments={"arg": "value"}
    )
    return MockLLMProvider(tool_calls=[tool_call])
