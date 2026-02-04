"""Tests for ToolRegistry - Tool configuration management."""

import tempfile
from pathlib import Path

import pytest

from agenix.extensions.tool_registry import ToolConfig, ToolRegistry


class TestToolConfig:
    """Test ToolConfig dataclass."""

    def test_create_basic_tool_config(self):
        """Test creating basic tool config."""
        config = ToolConfig(
            name="read",
            description="Read a file",
            module="agenix.tools.read",
            class_name="ReadTool"
        )

        assert config.name == "read"
        assert config.description == "Read a file"
        assert config.module == "agenix.tools.read"
        assert config.class_name == "ReadTool"

    def test_tool_config_with_parameters(self):
        """Test tool config with parameters."""
        config = ToolConfig(
            name="write",
            description="Write a file",
            module="agenix.tools.write",
            class_name="WriteTool",
            parameters={"max_size": 1024}
        )

        assert config.parameters == {"max_size": 1024}

    def test_tool_config_metadata(self):
        """Test tool config metadata fields."""
        config = ToolConfig(
            name="read",
            description="Read",
            module="agenix.tools.read",
            class_name="ReadTool",
            source_file=Path("/tmp/tool.md"),
            is_builtin=True
        )

        assert config.source_file == Path("/tmp/tool.md")
        assert config.is_builtin is True


class TestToolRegistry:
    """Test ToolRegistry class."""

    def test_registry_initialization(self):
        """Test registry initialization."""
        ToolRegistry.reset()
        ToolRegistry.initialize()

        assert ToolRegistry._initialized

    def test_list_tools(self):
        """Test listing all tools."""
        ToolRegistry.reset()
        ToolRegistry.initialize()

        tools = ToolRegistry.list()

        # Should return a list
        assert isinstance(tools, list)

    def test_list_names(self):
        """Test listing tool names."""
        ToolRegistry.reset()
        ToolRegistry.initialize()

        names = ToolRegistry.list_names()

        # Should return a list of strings
        assert isinstance(names, list)
        assert all(isinstance(n, str) for n in names)

    def test_get_tool(self):
        """Test getting a tool."""
        ToolRegistry.reset()
        ToolRegistry.initialize()

        # Try to get any existing tool
        tools = ToolRegistry.list()
        if tools:
            tool = ToolRegistry.get(tools[0].name)
            assert tool is not None
            assert tool.name == tools[0].name

    def test_get_nonexistent_tool(self):
        """Test getting tool that doesn't exist."""
        ToolRegistry.reset()
        ToolRegistry.initialize()

        tool = ToolRegistry.get("nonexistent_tool_12345")

        assert tool is None

    def test_exists(self):
        """Test checking if tool exists."""
        ToolRegistry.reset()
        ToolRegistry.initialize()

        # Test with nonexistent tool
        assert not ToolRegistry.exists("definitely-nonexistent-tool-12345")

    def test_reset_registry(self):
        """Test resetting the registry."""
        ToolRegistry.reset()
        ToolRegistry.initialize()

        # After reset, should be empty
        ToolRegistry.reset()

        assert len(ToolRegistry._tools) == 0
        assert not ToolRegistry._initialized


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
