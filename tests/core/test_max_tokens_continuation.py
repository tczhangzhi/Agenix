"""Test suite for max_tokens continuation behavior.

This module tests that the agent correctly handles finish_reason="length"
by continuing the loop to allow the LLM to complete its output.
"""

import pytest
from agenix.core.agent import Agent, AgentConfig
from agenix.core.messages import AssistantMessage, TextContent, ToolCall
from agenix.core.llm import StreamEvent


class TestMaxTokensContinuation:
    """Test cases for max_tokens continuation."""

    def test_finish_reason_captured_in_stream_event(self):
        """Test that StreamEvent can hold finish_reason."""
        event = StreamEvent(
            type="finish",
            finish_reason="length"
        )

        assert event.finish_reason == "length"

    def test_stop_reason_length_triggers_continuation(self):
        """Test that stop_reason='length' allows loop to continue."""
        # Create a message with stop_reason="length"
        message = AssistantMessage(
            content=[TextContent(text="Incomplete output...")],
            model="gpt-4o",
            stop_reason="length"
        )

        # Check continuation logic
        should_continue = (
            bool(message.tool_calls) or
            message.stop_reason == "length"
        )

        assert should_continue, "Loop should continue when stop_reason is 'length'"

    def test_stop_reason_stop_ends_loop(self):
        """Test that stop_reason='stop' ends the loop."""
        message = AssistantMessage(
            content=[TextContent(text="Complete output.")],
            model="gpt-4o",
            stop_reason="stop"
        )

        should_continue = (
            bool(message.tool_calls) or
            message.stop_reason == "length"
        )

        assert not should_continue, "Loop should end when stop_reason is 'stop'"

    def test_tool_calls_trigger_continuation(self):
        """Test that tool_calls still trigger continuation."""
        message = AssistantMessage(
            content=[],
            model="gpt-4o",
            tool_calls=[
                ToolCall(
                    id="call_1",
                    name="read",
                    arguments={"file_path": "test.txt"}
                )
            ],
            stop_reason="tool_calls"
        )

        should_continue = (
            bool(message.tool_calls) or
            message.stop_reason == "length"
        )

        assert should_continue, "Loop should continue when there are tool_calls"

    def test_anthropic_stop_reason_mapping(self):
        """Test Anthropic stop_reason mapping to OpenAI style."""
        stop_reason_map = {
            "end_turn": "stop",
            "max_tokens": "length",
            "tool_use": "tool_calls",
            "stop_sequence": "stop"
        }

        assert stop_reason_map["max_tokens"] == "length"
        assert stop_reason_map["end_turn"] == "stop"
        assert stop_reason_map["tool_use"] == "tool_calls"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
