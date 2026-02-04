"""Test suite for tools.bash module.

This module contains unit tests for the bash command execution tool.
"""

import pytest

from agenix.tools.bash import BashTool


class TestBashTool:
    """Test cases for BashTool class."""

    def test_create_bash_tool(self):
        """Test creating a bash tool instance."""
        tool = BashTool(working_dir=".", timeout=60)

        assert tool.name == "bash"
        assert "bash" in tool.description.lower()
        assert "command" in tool.parameters["properties"]

    @pytest.mark.asyncio
    async def test_execute_simple_command(self):
        """Test executing a simple command."""
        tool = BashTool(working_dir=".")

        result = await tool.execute(
            tool_call_id="call_123",
            arguments={"command": "echo hello"}
        )

        assert result.is_error is False
        assert "hello" in result.content.lower()
        assert result.details["exit_code"] == 0

    @pytest.mark.asyncio
    async def test_execute_command_with_output(self):
        """Test command with stdout output."""
        tool = BashTool(working_dir=".")

        result = await tool.execute(
            tool_call_id="call_123",
            arguments={"command": "echo 'test output'"}
        )

        assert "test output" in result.content

    @pytest.mark.asyncio
    async def test_execute_failing_command(self):
        """Test command that fails."""
        tool = BashTool(working_dir=".")

        result = await tool.execute(
            tool_call_id="call_123",
            arguments={"command": "exit 1"}
        )

        assert result.is_error is True
        assert result.details["exit_code"] == 1

    @pytest.mark.asyncio
    async def test_execute_nonexistent_command(self):
        """Test executing a command that doesn't exist."""
        tool = BashTool(working_dir=".")

        result = await tool.execute(
            tool_call_id="call_123",
            arguments={"command": "nonexistent_command_xyz"}
        )

        # Should either be error or non-zero exit code
        assert result.is_error is True or result.details.get("exit_code") != 0

    @pytest.mark.asyncio
    async def test_working_directory(self):
        """Test that command executes in correct working directory."""
        import os
        import tempfile

        temp_dir = tempfile.mkdtemp()
        try:
            tool = BashTool(working_dir=temp_dir)

            result = await tool.execute(
                tool_call_id="call_123",
                arguments={"command": "pwd"}
            )

            assert temp_dir in result.content
        finally:
            os.rmdir(temp_dir)

    @pytest.mark.asyncio
    async def test_command_with_stderr(self):
        """Test command that writes to stderr."""
        tool = BashTool(working_dir=".")

        result = await tool.execute(
            tool_call_id="call_123",
            arguments={"command": "echo 'error' >&2"}
        )

        # Should capture stderr
        assert "Stderr" in result.content or "error" in result.content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
