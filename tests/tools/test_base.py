"""Test suite for tools.base module.

This module contains unit tests for the base Tool interface.
"""

import pytest

from agenix.core.messages import TextContent
from agenix.tools.base import Tool, ToolResult


class DummyTool(Tool):
    """A dummy tool for testing purposes."""

    async def execute(self, tool_call_id, arguments, on_update=None):
        """Execute the dummy tool."""
        return ToolResult(content="dummy result")


class TestToolResult:
    """Test cases for ToolResult dataclass."""

    def test_create_tool_result(self):
        """Test creating a basic tool result."""
        result = ToolResult(content="Test output")

        assert result.content == "Test output"
        assert result.details is None
        assert result.is_error is False

    def test_create_tool_result_with_details(self):
        """Test creating tool result with details."""
        result = ToolResult(
            content="Output",
            details={"lines": 10, "path": "/test"},
            is_error=False
        )

        assert result.details["lines"] == 10
        assert result.details["path"] == "/test"

    def test_create_error_result(self):
        """Test creating an error result."""
        result = ToolResult(
            content="Error message",
            is_error=True
        )

        assert result.is_error is True


class TestTool:
    """Test cases for Tool base class."""

    def test_create_tool(self):
        """Test creating a tool instance."""
        tool = DummyTool(
            name="test",
            description="A test tool",
            parameters={"type": "object"}
        )

        assert tool.name == "test"
        assert tool.description == "A test tool"
        assert tool.parameters["type"] == "object"

    def test_to_dict(self):
        """Test converting tool to dictionary."""
        tool = DummyTool(
            name="test",
            description="A test tool",
            parameters={
                "type": "object",
                "properties": {
                    "arg1": {"type": "string"}
                }
            }
        )

        tool_dict = tool.to_dict()

        assert tool_dict["name"] == "test"
        assert tool_dict["description"] == "A test tool"
        assert "properties" in tool_dict["parameters"]

    def test_validate_arguments_success(self):
        """Test validating correct arguments."""
        tool = DummyTool(
            name="test",
            description="Test",
            parameters={
                "type": "object",
                "required": ["arg1", "arg2"]
            }
        )

        # Should not raise
        tool.validate_arguments({"arg1": "value1", "arg2": "value2"})

    def test_validate_arguments_missing_required(self):
        """Test validating arguments with missing required field."""
        tool = DummyTool(
            name="test",
            description="Test",
            parameters={
                "type": "object",
                "required": ["arg1", "arg2"]
            }
        )

        with pytest.raises(ValueError, match="Missing required argument"):
            tool.validate_arguments({"arg1": "value1"})

    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """Test executing a tool."""
        tool = DummyTool(
            name="test",
            description="Test",
            parameters={}
        )

        result = await tool.execute(
            tool_call_id="call_123",
            arguments={}
        )

        assert result.content == "dummy result"
        assert result.is_error is False

    @pytest.mark.asyncio
    async def test_execute_with_callback(self):
        """Test executing tool with progress callback."""
        updates = []

        def on_update(msg):
            updates.append(msg)

        tool = DummyTool(
            name="test",
            description="Test",
            parameters={}
        )

        result = await tool.execute(
            tool_call_id="call_123",
            arguments={},
            on_update=on_update
        )

        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
