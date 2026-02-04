"""Test suite for tools.grep module.

This module contains unit tests for the grep search tool.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from agenix.tools.grep import GrepTool


class TestGrepTool:
    """Test cases for GrepTool class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)

    def test_create_grep_tool(self):
        """Test creating a grep tool instance."""
        tool = GrepTool(working_dir=".")

        assert tool.name == "grep"
        assert "Search" in tool.description or "search" in tool.description
        assert "pattern" in tool.parameters["properties"]

    @pytest.mark.asyncio
    async def test_simple_search(self):
        """Test simple pattern search."""
        self.setUp()
        try:
            # Create test files
            (Path(self.temp_dir) / "test1.txt").write_text("Hello World\nGoodbye")
            (Path(self.temp_dir) / "test2.txt").write_text("Hello Python")

            tool = GrepTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={"pattern": "Hello"}
            )

            assert result.is_error is False
            assert "Hello" in result.content
            # Should find matches in both files
            assert "test1.txt" in result.content or "test2.txt" in result.content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_regex_search(self):
        """Test regex pattern search."""
        self.setUp()
        try:
            (Path(self.temp_dir) /
             "test.py").write_text("def function1():\ndef function2():\n")

            tool = GrepTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={"pattern": r"def \w+\(\):"}
            )

            assert result.is_error is False
            assert "function1" in result.content or "function2" in result.content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_file_pattern_filter(self):
        """Test filtering by file pattern."""
        self.setUp()
        try:
            (Path(self.temp_dir) / "test.py").write_text("import os")
            (Path(self.temp_dir) / "test.txt").write_text("import os")

            tool = GrepTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "pattern": "import",
                    "file_pattern": "*.py"
                }
            )

            assert result.is_error is False
            assert "test.py" in result.content
            # Should not include .txt file
            assert "test.txt" not in result.content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_case_insensitive_search(self):
        """Test case insensitive search."""
        self.setUp()
        try:
            (Path(self.temp_dir) / "test.txt").write_text("Hello WORLD")

            tool = GrepTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "pattern": "hello",
                    "ignore_case": True
                }
            )

            assert result.is_error is False
            assert "Hello" in result.content or "WORLD" in result.content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_no_matches_found(self):
        """Test when no matches are found."""
        self.setUp()
        try:
            (Path(self.temp_dir) / "test.txt").write_text("Hello World")

            tool = GrepTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={"pattern": "nonexistent"}
            )

            assert result.is_error is False
            assert "No matches found" in result.content or "0" in result.content
        finally:
            self.tearDown()

    @pytest.mark.asyncio
    async def test_max_results_limit(self):
        """Test that max results limit is respected."""
        self.setUp()
        try:
            # Create file with many matching lines
            content = "\n".join([f"match line {i}" for i in range(200)])
            (Path(self.temp_dir) / "test.txt").write_text(content)

            tool = GrepTool(working_dir=self.temp_dir)
            result = await tool.execute(
                tool_call_id="call_123",
                arguments={
                    "pattern": "match",
                    "max_results": 10
                }
            )

            # Should find at most 10 results
            match_count = result.content.count("match line")
            assert match_count <= 10
        finally:
            self.tearDown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
