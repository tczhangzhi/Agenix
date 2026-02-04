"""Test suite for tools.write module.

This module contains unit tests for the write file tool.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from agenix.tools.write import WriteTool


class TestWriteTool:
    """Test cases for WriteTool class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)

    def test_create_write_tool(self):
        """Test creating a write tool instance."""
        tool = WriteTool(working_dir=".")

        assert tool.name == "write"
        assert "Write" in tool.description
        assert "file_path" in tool.parameters["properties"]
        assert "content" in tool.parameters["properties"]

    @pytest.mark.asyncio
    async def test_write_simple_file(self):
        """Test writing a simple text file."""
        self.setUp()
        try:
            tool = WriteTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": "test.txt",
                    "content": "Hello World"
                }
            )

            assert result.is_error is False
            assert "Successfully wrote" in result.content

            # Verify file was created
            test_file = Path(self.temp_dir) / "test.txt"
            assert test_file.exists()
            assert test_file.read_text() == "Hello World"
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_write_multiline_file(self):
        """Test writing a file with multiple lines."""
        self.setUp()
        try:
            content = "Line 1\nLine 2\nLine 3"

            tool = WriteTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": "multiline.txt",
                    "content": content
                }
            )

            assert result.is_error is False

            # Verify content
            test_file = Path(self.temp_dir) / "multiline.txt"
            assert test_file.read_text() == content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_write_creates_parent_directories(self):
        """Test that write creates parent directories if needed."""
        self.setUp()
        try:
            tool = WriteTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": "subdir/nested/test.txt",
                    "content": "Nested file"
                }
            )

            assert result.is_error is False

            # Verify nested file was created
            test_file = Path(self.temp_dir) / "subdir" / "nested" / "test.txt"
            assert test_file.exists()
            assert test_file.read_text() == "Nested file"
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_write_overwrites_existing_file(self):
        """Test that write overwrites existing files."""
        self.setUp()
        try:
            test_file = Path(self.temp_dir) / "overwrite.txt"
            test_file.write_text("Original content")

            tool = WriteTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": "overwrite.txt",
                    "content": "New content"
                }
            )

            assert result.is_error is False
            assert test_file.read_text() == "New content"
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_write_with_absolute_path(self):
        """Test writing file with absolute path."""
        self.setUp()
        try:
            absolute_path = Path(self.temp_dir) / "absolute.txt"

            tool = WriteTool(working_dir=".")
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": str(absolute_path),
                    "content": "Absolute path test"
                }
            )

            assert result.is_error is False
            assert absolute_path.exists()
        finally:
            self.tearDown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
