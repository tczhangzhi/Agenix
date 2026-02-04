"""Tests for TaskTool - Subagent delegation tool (without mocks)."""

import tempfile
from pathlib import Path

import pytest

from agenix.tools.task import TaskTool


class TestTaskToolBasics:
    """Test basic TaskTool functionality."""

    def test_tool_initialization(self):
        """Test TaskTool initialization."""
        tool = TaskTool(agent_id="build")

        assert tool.name == "task"
        assert tool.agent_id == "build"
        assert "Delegate a task" in tool.description

    def test_tool_parameters_structure(self):
        """Test that tool has correct parameter structure."""
        tool = TaskTool()

        params = tool.parameters
        assert params["type"] == "object"
        assert "agent" in params["properties"]
        assert "task" in params["properties"]
        assert "context" in params["properties"]
        assert "agent" in params["required"]
        assert "task" in params["required"]

    def test_parent_agent_excluded_from_list(self):
        """Test that parent agent is excluded from available agents."""
        tool = TaskTool(agent_id="build")

        # Parent agent should not be in available agents
        if tool._available_agents:
            assert "build" not in tool._available_agents

    @pytest.mark.asyncio
    async def test_missing_agent_parameter(self):
        """Test error when agent parameter is missing."""
        tool = TaskTool()

        result = await tool.execute(
            tool_call_id="test1",
            arguments={"task": "Do something"}
        )

        assert result.is_error
        assert "agent parameter is required" in result.content

    @pytest.mark.asyncio
    async def test_missing_task_parameter(self):
        """Test error when task parameter is missing."""
        tool = TaskTool()

        result = await tool.execute(
            tool_call_id="test2",
            arguments={"agent": "explore"}
        )

        assert result.is_error
        assert "task parameter is required" in result.content

    @pytest.mark.asyncio
    async def test_empty_agent_name(self):
        """Test error with empty agent name."""
        tool = TaskTool()

        result = await tool.execute(
            tool_call_id="test3",
            arguments={"agent": "", "task": "Do something"}
        )

        assert result.is_error
        assert "agent parameter is required" in result.content

    @pytest.mark.asyncio
    async def test_empty_task(self):
        """Test error with empty task."""
        tool = TaskTool()

        result = await tool.execute(
            tool_call_id="test4",
            arguments={"agent": "explore", "task": ""}
        )

        assert result.is_error
        assert "task parameter is required" in result.content

    @pytest.mark.asyncio
    async def test_nonexistent_agent(self):
        """Test error when agent doesn't exist."""
        tool = TaskTool()

        result = await tool.execute(
            tool_call_id="test5",
            arguments={
                "agent": "nonexistent-agent",
                "task": "Do something"
            }
        )

        assert result.is_error
        assert "not found" in result.content

    def test_format_agents_description_empty(self):
        """Test agent description formatting with no agents."""
        tool = TaskTool()
        tool._available_agents = {}

        desc = tool._format_agents_description()

        assert "No subagents available" in desc

    def test_format_agents_description_with_agents(self):
        """Test agent description formatting with agents."""
        tool = TaskTool()
        tool._available_agents = {
            "explore": {"description": "Explores code", "model": "gpt-4"},
            "test": {"description": "Runs tests", "model": "gpt-3.5-turbo"}
        }

        desc = tool._format_agents_description()

        assert "Available subagents:" in desc
        assert "explore" in desc
        assert "Explores code" in desc
        assert "test" in desc
        assert "Runs tests" in desc

    def test_agent_registry_integration(self):
        """Test that tool integrates with agent registry."""
        tool = TaskTool()

        # Should have queried the registry
        assert isinstance(tool._available_agents, dict)

    def test_no_recursion_parent_excluded(self):
        """Test that parent agent can't delegate to itself."""
        tool = TaskTool(agent_id="build")

        # Parent should not be in available agents
        assert "build" not in tool._available_agents


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
