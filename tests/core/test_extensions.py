"""Tests for the extension system."""

import os
import tempfile
from pathlib import Path

import pytest

from agenix.extensions import (CommandDefinition, EventType, ExtensionContext,
                               ExtensionRunner, SessionStartEvent,
                               ToolCallEvent, ToolDefinition,
                               discover_and_load_extensions, load_extension)


@pytest.fixture
def temp_extension_dir():
    """Create a temporary directory for extensions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    class MockAgent:
        def __init__(self):
            self.messages = []
    return MockAgent()


@pytest.fixture
def extension_context(mock_agent):
    """Create an extension context."""
    return ExtensionContext(
        agent=mock_agent,
        cwd="/tmp",
        tools=[]
    )


class TestExtensionLoader:
    """Test extension loading."""

    @pytest.mark.asyncio
    async def test_load_simple_extension(self, temp_extension_dir):
        """Test loading a simple extension."""
        # Create a simple extension
        ext_file = os.path.join(temp_extension_dir, "test_ext.py")
        with open(ext_file, "w") as f:
            f.write("""
async def setup(agenix):
    from agenix.extensions import ToolDefinition

    async def my_tool(params, ctx):
        return "test result"

    agenix.register_tool(ToolDefinition(
        name="test_tool",
        description="A test tool",
        parameters={"type": "object"},
        execute=my_tool
    ))
""")

        # Load the extension
        extension = await load_extension(ext_file)

        # Verify
        assert extension is not None
        assert extension.name == "test_ext"
        assert "test_tool" in extension.tools

    @pytest.mark.asyncio
    async def test_discover_extensions(self, temp_extension_dir):
        """Test extension discovery."""
        # Create .agenix/extensions directory structure
        project_ext_dir = os.path.join(
            temp_extension_dir, ".agenix", "extensions")
        os.makedirs(project_ext_dir)

        # Create multiple extensions
        for i in range(3):
            ext_file = os.path.join(project_ext_dir, f"ext{i}.py")
            with open(ext_file, "w") as f:
                f.write(f"""
async def setup(agenix):
    pass
""")

        # Discover extensions
        extensions = await discover_and_load_extensions(
            cwd=temp_extension_dir,
            agenix_dir="/nonexistent"  # Don't use real global dir
        )

        # Should find 3 extensions from project dir
        assert len(extensions) == 3

    @pytest.mark.asyncio
    async def test_extension_with_event_handler(self, temp_extension_dir):
        """Test extension with event handlers."""
        ext_file = os.path.join(temp_extension_dir, "events.py")
        with open(ext_file, "w") as f:
            f.write("""
from agenix.extensions import EventType

async def setup(agenix):
    @agenix.on(EventType.SESSION_START)
    async def on_start(event, ctx):
        pass
""")

        extension = await load_extension(ext_file)

        assert extension is not None
        assert EventType.SESSION_START in extension.handlers
        assert len(extension.handlers[EventType.SESSION_START]) == 1

    @pytest.mark.asyncio
    async def test_extension_with_command(self, temp_extension_dir):
        """Test extension with command."""
        ext_file = os.path.join(temp_extension_dir, "commands.py")
        with open(ext_file, "w") as f:
            f.write("""
from agenix.extensions import CommandDefinition

async def setup(agenix):
    async def stats_handler(ctx, args):
        pass

    agenix.register_command(CommandDefinition(
        name="stats",
        description="Show stats",
        handler=stats_handler
    ))
""")

        extension = await load_extension(ext_file)

        assert extension is not None
        assert "stats" in extension.commands


class TestExtensionRunner:
    """Test extension runner."""

    @pytest.mark.asyncio
    async def test_emit_event(self, temp_extension_dir, extension_context):
        """Test event emission."""
        # Create extension with event handler
        ext_file = os.path.join(temp_extension_dir, "test.py")
        with open(ext_file, "w") as f:
            f.write("""
from agenix.extensions import EventType

events_received = []

async def setup(agenix):
    @agenix.on(EventType.SESSION_START)
    async def on_start(event, ctx):
        events_received.append(event.type)
""")

        extensions = [await load_extension(ext_file)]
        runner = ExtensionRunner(extensions, extension_context)

        # Emit event
        await runner.emit(SessionStartEvent())

        # Can't easily verify due to module isolation, but test runs without error

    @pytest.mark.asyncio
    async def test_get_tools(self, temp_extension_dir, extension_context):
        """Test getting registered tools."""
        ext_file = os.path.join(temp_extension_dir, "tools.py")
        with open(ext_file, "w") as f:
            f.write("""
from agenix.extensions import ToolDefinition

async def setup(agenix):
    async def tool1(params, ctx):
        return "result1"

    async def tool2(params, ctx):
        return "result2"

    agenix.register_tool(ToolDefinition(
        name="tool1",
        description="Tool 1",
        parameters={"type": "object"},
        execute=tool1
    ))

    agenix.register_tool(ToolDefinition(
        name="tool2",
        description="Tool 2",
        parameters={"type": "object"},
        execute=tool2
    ))
""")

        extensions = [await load_extension(ext_file)]
        runner = ExtensionRunner(extensions, extension_context)

        tools = runner.get_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools

    @pytest.mark.asyncio
    async def test_execute_command(self, temp_extension_dir, extension_context):
        """Test command execution."""
        ext_file = os.path.join(temp_extension_dir, "cmd.py")
        with open(ext_file, "w") as f:
            f.write("""
from agenix.extensions import CommandDefinition

executed = []

async def setup(agenix):
    async def my_cmd(ctx, args):
        executed.append(args)

    agenix.register_command(CommandDefinition(
        name="mycmd",
        description="My command",
        handler=my_cmd
    ))
""")

        extensions = [await load_extension(ext_file)]
        runner = ExtensionRunner(extensions, extension_context)

        # Execute command
        result = await runner.execute_command("mycmd", "test args")
        assert result is True  # Command was found

        # Unknown command
        result = await runner.execute_command("unknown", "args")
        assert result is False


class TestExtensionContext:
    """Test extension context."""

    def test_context_properties(self, mock_agent):
        """Test context provides access to agent state."""
        ctx = ExtensionContext(
            agent=mock_agent,
            cwd="/test/dir",
            tools=[]
        )

        assert ctx.agent == mock_agent
        assert ctx.cwd == "/test/dir"
        assert ctx.messages == []

    def test_notify(self, mock_agent, capsys):
        """Test notification output."""
        ctx = ExtensionContext(
            agent=mock_agent,
            cwd="/tmp",
            tools=[]
        )

        ctx.notify("Test message", "info")
        captured = capsys.readouterr()
        assert "Test message" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
