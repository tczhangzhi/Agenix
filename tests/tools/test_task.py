"""Tests for TaskTool - Subagent delegation tool (without mocks)."""

import tempfile
from pathlib import Path

import pytest

from agenix.tools.task import TaskTool


class TestTaskToolBasics:
    """Test basic TaskTool functionality."""

    def test_tool_initialization(self):
        """Test TaskTool initialization."""
        tool = TaskTool(agent_id="main-agent")

        assert tool.name == "task"
        assert tool.agent_id == "main-agent"
        assert "Delegate a task" in tool.description

    def test_tool_parameters_structure(self):
        """Test that tool has correct parameter structure."""
        tool = TaskTool()

        params = tool.parameters
        assert params["type"] == "object"
        assert "task" in params["properties"]
        assert "context" in params["properties"]
        assert "task" in params["required"]

    @pytest.mark.asyncio
    async def test_missing_task_parameter(self):
        """Test error when task parameter is missing."""
        tool = TaskTool()

        result = await tool.execute(
            tool_call_id="test2",
            arguments={}
        )

        assert result.is_error
        assert "task parameter is required" in result.content

    @pytest.mark.asyncio
    async def test_empty_task(self):
        """Test error with empty task."""
        tool = TaskTool()

        result = await tool.execute(
            tool_call_id="test4",
            arguments={"task": ""}
        )

        assert result.is_error
        assert "task parameter is required" in result.content

    def test_parent_chain_tracking(self):
        """Test that parent chain is properly tracked."""
        parent_chain = ["agent1", "agent2"]
        tool = TaskTool(
            agent_id="agent3",
            parent_chain=parent_chain
        )

        assert tool.parent_chain == parent_chain
        assert tool.agent_id == "agent3"

    @pytest.mark.asyncio
    async def test_circular_call_detection(self):
        """Test that circular agent calls are detected."""
        # Create a tool with agent_id that's in its own parent chain
        tool = TaskTool(
            agent_id="agent1",
            parent_chain=["agent1"]  # agent1 is in its own parent chain - circular!
        )

        result = await tool.execute(
            tool_call_id="test_circular",
            arguments={"task": "Do something"}
        )

        assert result.is_error
        assert "Circular agent call" in result.content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
