"""Tests for the SDK (programmatic API)."""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agenix.core.messages import MessageEndEvent, MessageUpdateEvent
from agenix.sdk import AgentSession, create_session


class TestSDK:
    """Test SDK functionality."""

    @pytest.mark.asyncio
    async def test_create_session_with_api_key(self):
        """Test creating a session with explicit API key."""
        session = await create_session(
            api_key="test-key",
            model="gpt-4o",
            enable_extensions=False  # Disable for simpler test
        )

        assert session is not None
        assert isinstance(session, AgentSession)
        assert session.agent is not None

    @pytest.mark.asyncio
    async def test_create_session_from_env(self, monkeypatch):
        """Test creating a session using environment variable."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-test-key")

        session = await create_session(
            model="gpt-4o",
            enable_extensions=False
        )

        assert session is not None

    @pytest.mark.asyncio
    async def test_create_session_no_api_key(self, monkeypatch):
        """Test that session creation fails without API key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(ValueError, match="API key required"):
            await create_session(enable_extensions=False)

    @pytest.mark.asyncio
    async def test_session_get_messages(self):
        """Test getting conversation messages."""
        session = await create_session(
            api_key="test-key",
            model="gpt-4o",
            enable_extensions=False
        )

        # Initially empty
        messages = session.get_messages()
        assert messages == []

    @pytest.mark.asyncio
    async def test_session_clear_messages(self):
        """Test clearing conversation messages."""
        session = await create_session(
            api_key="test-key",
            model="gpt-4o",
            enable_extensions=False
        )

        # Add some mock messages
        from agenix.core.messages import UserMessage
        session.agent.messages.append(UserMessage(content="test"))

        # Clear
        session.clear_messages()

        # Verify cleared
        assert len(session.get_messages()) == 0

    @pytest.mark.asyncio
    async def test_session_working_dir(self):
        """Test session respects working directory."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            session = await create_session(
                api_key="test-key",
                model="gpt-4o",
                working_dir=tmpdir,
                enable_extensions=False
            )

            assert session.working_dir == tmpdir

    @pytest.mark.asyncio
    async def test_session_close(self):
        """Test session cleanup."""
        session = await create_session(
            api_key="test-key",
            model="gpt-4o",
            enable_extensions=False
        )

        # Should not raise
        await session.close()

    @pytest.mark.asyncio
    async def test_session_with_extensions(self, monkeypatch):
        """Test session with extensions enabled."""
        # Mock extension loading to avoid filesystem dependencies
        async def mock_load_extensions(cwd):
            return []

        with patch('agenix.sdk.discover_and_load_extensions', new=mock_load_extensions):
            session = await create_session(
                api_key="test-key",
                model="gpt-4o",
                enable_extensions=True
            )

            assert session is not None


class TestAgentSession:
    """Test AgentSession class."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        agent = MagicMock()
        agent.messages = []
        agent.clear_messages = MagicMock()
        return agent

    @pytest.fixture
    def session(self, mock_agent):
        """Create a test session."""
        return AgentSession(
            agent=mock_agent,
            tools=[],
            extension_runner=None,
            working_dir="/tmp"
        )

    @pytest.mark.asyncio
    async def test_prompt_collects_response(self, session, mock_agent):
        """Test that prompt() collects the response text."""
        # Mock the agent.prompt to return events
        async def mock_prompt(message):
            yield MessageUpdateEvent(message=None, delta="Hello ")
            yield MessageUpdateEvent(message=None, delta="world!")
            yield MessageEndEvent(message=None)

        mock_agent.prompt = mock_prompt

        response = await session.prompt("test")
        assert response == "Hello world!"

    def test_get_messages(self, session, mock_agent):
        """Test get_messages returns agent messages."""
        from agenix.core.messages import UserMessage

        mock_agent.messages = [UserMessage(content="test")]

        messages = session.get_messages()
        assert len(messages) == 1
        assert messages[0].content == "test"

    def test_clear_messages(self, session, mock_agent):
        """Test clear_messages calls agent method."""
        session.clear_messages()
        mock_agent.clear_messages.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
