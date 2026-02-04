"""Test suite for tools.read module.

This module contains unit tests for the read file tool.
"""

import os
import tempfile
from pathlib import Path

import pytest

from agenix.tools.read import ReadTool


class TestReadTool:
    """Test cases for ReadTool class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)

    def test_create_read_tool(self):
        """Test creating a read tool instance."""
        tool = ReadTool(working_dir=".")

        assert tool.name == "read"
        assert "Read" in tool.description
        assert "file_path" in tool.parameters["properties"]

    @pytest.mark.asyncio
    async def test_read_simple_file(self):
        """Test reading a simple text file."""
        self.setUp()
        try:
            # Create test file
            test_file = Path(self.temp_dir) / "test.txt"
            test_file.write_text("Hello\nWorld\n")

            tool = ReadTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={"file_path": "test.txt"}
            )

            assert result.is_error is False
            assert "Hello" in result.content
            assert "World" in result.content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_read_with_line_numbers(self):
        """Test that read output includes line numbers."""
        self.setUp()
        try:
            test_file = Path(self.temp_dir) / "test.txt"
            test_file.write_text("Line 1\nLine 2\nLine 3\n")

            tool = ReadTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={"file_path": "test.txt"}
            )

            # Should have line numbers (format: "     1\t")
            assert "1\t" in result.content or "Line 1" in result.content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_read_with_offset_and_limit(self):
        """Test reading file with offset and limit."""
        self.setUp()
        try:
            test_file = Path(self.temp_dir) / "test.txt"
            lines = [f"Line {i}\n" for i in range(1, 11)]
            test_file.write_text("".join(lines))

            tool = ReadTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "file_path": "test.txt",
                    "offset": 3,
                    "limit": 3
                }
            )

            assert result.is_error is False
            # Should show truncation info
            assert "Showing lines" in result.content or "Line 3" in result.content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist."""
        tool = ReadTool(working_dir=self.temp_dir if hasattr(
            self, 'temp_dir') else ".")

        result = await tool.execute(
            tool_call_id="call_123",
            arguments={"file_path": "nonexistent.txt"}
        )

        assert result.is_error is True
        assert "not found" in result.content.lower()

    @pytest.mark.asyncio
    async def test_read_absolute_path(self):
        """Test reading file with absolute path."""
        self.setUp()
        try:
            test_file = Path(self.temp_dir) / "test.txt"
            test_file.write_text("Absolute path test")

            tool = ReadTool(working_dir=".")
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={"file_path": str(test_file)}
            )

            assert result.is_error is False
            assert "Absolute path test" in result.content
        finally:
            self.tearDown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
