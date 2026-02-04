"""Test suite for tools.edit module.

This module contains unit tests for the edit file tool.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from agenix.tools.edit import EditTool


class TestEditTool:
    """Test cases for EditTool class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)

    def test_create_edit_tool(self):
        """Test creating an edit tool instance."""
        tool = EditTool(working_dir=".")

        assert tool.name == "edit"
        assert "Edit" in tool.description
        assert "file_path" in tool.parameters["properties"]
        assert "old_string" in tool.parameters["properties"]
        assert "new_string" in tool.parameters["properties"]

    @pytest.mark.asyncio
    async def test_simple_edit(self):
        """Test simple string replacement."""
        self.setUp()
        try:
            # Create test file
            test_file = Path(self.temp_dir) / "test.py"
            test_file.write_text("def old_function():\n    pass\n")

            tool = EditTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": "test.py",
                    "old_string": "old_function",
                    "new_string": "new_function"
                }
            )

            assert result.is_error is False
            assert "Successfully replaced" in result.content

            # Verify edit
            content = test_file.read_text()
            assert "new_function" in content
            assert "old_function" not in content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_edit_preserves_whitespace(self):
        """Test that edit preserves exact whitespace."""
        self.setUp()
        try:
            test_file = Path(self.temp_dir) / "test.py"
            original = "def function():\n    return 42\n"
            test_file.write_text(original)

            tool = EditTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": "test.py",
                    "old_string": "    return 42",
                    "new_string": "    return 100"
                }
            )

            assert result.is_error is False
            content = test_file.read_text()
            assert "return 100" in content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_edit_generates_diff(self):
        """Test that edit generates a diff."""
        self.setUp()
        try:
            test_file = Path(self.temp_dir) / "test.txt"
            test_file.write_text("Hello World")

            tool = EditTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": "test.txt",
                    "old_string": "World",
                    "new_string": "Python"
                }
            )

            # Check that details include diff
            assert result.details is not None
            assert "diff" in result.details
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_edit_string_not_found(self):
        """Test edit when old_string is not found."""
        self.setUp()
        try:
            test_file = Path(self.temp_dir) / "test.txt"
            test_file.write_text("Hello World")

            tool = EditTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": "test.txt",
                    "old_string": "Goodbye",
                    "new_string": "Hello"
                }
            )

            assert result.is_error is True
            assert "could not find" in result.content.lower()
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_edit_replace_all(self):
        """Test replacing all occurrences."""
        self.setUp()
        try:
            test_file = Path(self.temp_dir) / "test.txt"
            test_file.write_text("foo bar foo baz foo")

            tool = EditTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": "test.txt",
                    "old_string": "foo",
                    "new_string": "qux",
                    "replace_all": True
                }
            )

            assert result.is_error is False
            content = test_file.read_text()
            assert content.count("qux") == 3
            assert "foo" not in content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_edit_replace_first_only(self):
        """Test replacing only first occurrence."""
        self.setUp()
        try:
            test_file = Path(self.temp_dir) / "test.txt"
            test_file.write_text("foo bar foo baz")

            tool = EditTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": "test.txt",
                    "old_string": "foo",
                    "new_string": "qux",
                    "replace_all": False
                }
            )

            assert result.is_error is False
            content = test_file.read_text()
            # Should have one qux and one remaining foo
            assert content.count("qux") == 1
            assert content.count("foo") == 1
        finally:
            self.tearDown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
