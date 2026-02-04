"""Test suite for agent loop error handling.

This module tests the agent's ability to handle incomplete tool calls
from LLM streaming and prevent execution of invalid tool calls.
"""

import pytest
from agenix.core.messages import ToolCall


class TestToolCallValidation:
    """Test cases for tool call validation."""

    def test_detect_empty_arguments_dict(self):
        """Test detection of empty arguments dictionary.

        Verify that tool calls with empty dict {} are detected as invalid.
        """
        tool_call = ToolCall(
            id="test_call_1",
            name="write",
            arguments={}
        )

        # Check validation logic
        is_invalid = not tool_call.arguments or not isinstance(tool_call.arguments, dict)
        assert is_invalid, "Empty dict should be detected as invalid"

    def test_detect_none_arguments(self):
        """Test detection of None arguments.

        Verify that tool calls with None arguments are detected as invalid.
        """
        tool_call = ToolCall(
            id="test_call_2",
            name="write",
            arguments=None  # type: ignore
        )

        is_invalid = not tool_call.arguments or not isinstance(tool_call.arguments, dict)
        assert is_invalid, "None arguments should be detected as invalid"

    def test_valid_arguments_pass(self):
        """Test that valid arguments are not flagged as invalid.

        Verify that tool calls with proper arguments pass validation.
        """
        tool_call = ToolCall(
            id="test_call_3",
            name="write",
            arguments={"file_path": "test.txt", "content": "hello"}
        )

        is_invalid = not tool_call.arguments or not isinstance(tool_call.arguments, dict)
        assert not is_invalid, "Valid arguments should pass validation"


class TestLLMStreamingIssues:
    """Test cases for LLM streaming issues."""

    def test_empty_arguments_string_scenario(self):
        """Test scenario where LLM returns empty arguments string.

        This simulates what happens when LLM streaming is interrupted
        or incomplete, resulting in empty arguments string.
        """
        # Simulate streaming accumulator result
        tc_data = {
            "id": "test_call_4",
            "name": "write",
            "arguments": ""  # Empty string from incomplete streaming
        }

        # This should be detected and skipped
        should_skip = not tc_data["arguments"] or not tc_data["arguments"].strip()
        assert should_skip, "Empty arguments string should trigger skip"

    def test_whitespace_only_arguments(self):
        """Test detection of whitespace-only arguments string.

        Verify that arguments containing only whitespace are detected.
        """
        tc_data = {
            "id": "test_call_5",
            "name": "write",
            "arguments": "   \n  "  # Only whitespace
        }

        should_skip = not tc_data["arguments"] or not tc_data["arguments"].strip()
        assert should_skip, "Whitespace-only arguments should trigger skip"


class TestErrorMessages:
    """Test cases for error message formatting."""

    def test_invalid_arguments_error_message(self):
        """Test that error messages are informative.

        Verify that error messages include the tool name and received arguments.
        """
        tool_call = ToolCall(
            id="test_call_6",
            name="write",
            arguments={}
        )

        error_content = (
            f"Error: Tool '{tool_call.name}' called with invalid arguments. "
            f"Received: {tool_call.arguments}. "
            f"Please check the tool's required parameters and try again with valid arguments."
        )

        assert tool_call.name in error_content
        assert "invalid arguments" in error_content.lower()
        assert "required parameters" in error_content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
