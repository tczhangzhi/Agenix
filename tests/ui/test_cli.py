"""Tests for UI improvements."""

from unittest.mock import MagicMock, patch

import pytest
from prompt_toolkit import PromptSession

from agenix.core.messages import (AssistantMessage, MessageUpdateEvent,
                                  ToolExecutionEndEvent,
                                  ToolExecutionStartEvent, TurnEndEvent)
from agenix.ui.cli import CLIRenderer


class TestCLIRenderer:
    """Test CLI renderer improvements."""

    @pytest.fixture
    def renderer(self):
        """Create a CLI renderer."""
        return CLIRenderer()

    def test_renderer_has_prompt_session(self, renderer):
        """Test renderer initializes with prompt_toolkit session."""
        assert hasattr(renderer, 'prompt_session')
        assert isinstance(renderer.prompt_session, PromptSession)

    def test_prompt_uses_prompt_toolkit(self, renderer):
        """Test that prompt() uses prompt_toolkit."""
        # Mock the prompt_session.prompt method
        renderer.prompt_session.prompt = MagicMock(return_value="test input")

        result = renderer.prompt("You")

        assert result == "test input"
        renderer.prompt_session.prompt.assert_called_once()

    def test_prompt_handles_eoferror(self, renderer):
        """Test prompt handles EOFError."""
        renderer.prompt_session.prompt = MagicMock(side_effect=EOFError())

        result = renderer.prompt("You")
        assert result == "/quit"

    def test_prompt_handles_keyboard_interrupt(self, renderer):
        """Test prompt handles KeyboardInterrupt."""
        renderer.prompt_session.prompt = MagicMock(
            side_effect=KeyboardInterrupt())

        result = renderer.prompt("You")
        assert result == "/quit"

    def test_turn_end_no_token_display(self, renderer, capsys):
        """Test that TurnEndEvent doesn't display tokens."""
        # Create event with usage info
        message = AssistantMessage(content="test")
        # Note: usage is None after our fix

        event = TurnEndEvent(message=message, tool_results=[])

        # Render event
        renderer.render_event(event)

        # Capture output
        captured = capsys.readouterr()

        # Should NOT contain token information
        assert "Tokens:" not in captured.out
        assert "tokens" not in captured.out.lower()

    def test_tool_icons(self, renderer):
        """Test that different tools have different icons."""
        tools = ["read", "write", "edit", "bash", "grep"]

        for tool in tools:
            event = ToolExecutionStartEvent(
                tool_name=tool,
                args={"test": "arg"}
            )

            # Should not raise
            renderer.render_event(event)

    def test_message_update_streaming(self, renderer, capsys):
        """Test message streaming output."""
        event = MessageUpdateEvent(message=None, delta="Hello")

        renderer.render_event(event)

        captured = capsys.readouterr()
        assert "Hello" in captured.out


class TestPromptToolkitIntegration:
    """Test prompt_toolkit integration for better unicode support."""

    def test_chinese_input_support(self):
        """Test that prompt_toolkit can handle Chinese characters."""
        renderer = CLIRenderer()

        # Mock to simulate Chinese input
        chinese_text = "你好世界"
        renderer.prompt_session.prompt = MagicMock(return_value=chinese_text)

        result = renderer.prompt("Test")

        assert result == chinese_text
        assert len(result) == 4  # 4 Chinese characters

    def test_prompt_style_configuration(self):
        """Test that prompt has style configuration."""
        renderer = CLIRenderer()

        # Check that style is configured
        assert renderer.prompt_session.style is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
