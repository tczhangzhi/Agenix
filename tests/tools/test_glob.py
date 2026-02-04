"""Tests for GlobTool - File pattern matching tool."""

import os
import tempfile
from pathlib import Path

import pytest

from agenix.tools.glob import GlobTool


class TestGlobTool:
    """Test cases for GlobTool."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create test file structure
            (tmp_path / "file1.py").touch()
            (tmp_path / "file2.py").touch()
            (tmp_path / "test.txt").touch()
            (tmp_path / "data.json").touch()

            # Create subdirectories
            (tmp_path / "src").mkdir()
            (tmp_path / "src" / "main.py").touch()
            (tmp_path / "src" / "utils.py").touch()
            (tmp_path / "src" / "config.yaml").touch()

            (tmp_path / "tests").mkdir()
            (tmp_path / "tests" / "test_main.py").touch()
            (tmp_path / "tests" / "test_utils.py").touch()

            (tmp_path / "docs").mkdir()
            (tmp_path / "docs" / "readme.md").touch()
            (tmp_path / "docs" / "api.md").touch()

            # Create nested structure
            (tmp_path / "src" / "components").mkdir()
            (tmp_path / "src" / "components" / "button.js").touch()
            (tmp_path / "src" / "components" / "input.js").touch()

            yield tmp_path

    @pytest.mark.asyncio
    async def test_simple_pattern(self, temp_dir):
        """Test simple glob pattern matching."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test1",
            arguments={"pattern": "*.py"}
        )

        assert not result.is_error
        assert "file1.py" in result.content
        assert "file2.py" in result.content
        assert "test.txt" not in result.content

    @pytest.mark.asyncio
    async def test_recursive_pattern(self, temp_dir):
        """Test recursive glob pattern with **."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test2",
            arguments={"pattern": "**/*.py"}
        )

        assert not result.is_error
        assert "file1.py" in result.content
        assert "main.py" in result.content or "src/main.py" in result.content
        assert "test_main.py" in result.content or "tests/test_main.py" in result.content
        assert result.details["count"] >= 6  # At least 6 Python files

    @pytest.mark.asyncio
    async def test_nested_recursive_pattern(self, temp_dir):
        """Test recursive pattern in subdirectory."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test3",
            arguments={"pattern": "src/**/*.py"}
        )

        assert not result.is_error
        assert "main.py" in result.content or "src/main.py" in result.content
        assert "utils.py" in result.content or "src/utils.py" in result.content
        assert "test_main.py" not in result.content  # Not in src/

    @pytest.mark.asyncio
    async def test_specific_directory(self, temp_dir):
        """Test glob with specific path parameter."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test4",
            arguments={
                "pattern": "*.py",
                "path": str(temp_dir / "tests")
            }
        )

        assert not result.is_error
        assert "test_main.py" in result.content
        assert "test_utils.py" in result.content
        assert "file1.py" not in result.content  # Not in tests/

    @pytest.mark.asyncio
    async def test_file_extension_pattern(self, temp_dir):
        """Test pattern for specific file extensions."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test5",
            arguments={"pattern": "**/*.md"}
        )

        assert not result.is_error
        assert "readme.md" in result.content or "docs/readme.md" in result.content
        assert "api.md" in result.content or "docs/api.md" in result.content
        assert result.details["count"] == 2

    @pytest.mark.asyncio
    async def test_js_files_pattern(self, temp_dir):
        """Test finding JavaScript files."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test6",
            arguments={"pattern": "**/*.js"}
        )

        assert not result.is_error
        assert "button.js" in result.content
        assert "input.js" in result.content
        assert result.details["count"] == 2

    @pytest.mark.asyncio
    async def test_no_matches(self, temp_dir):
        """Test pattern that matches no files."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test7",
            arguments={"pattern": "*.nonexistent"}
        )

        assert not result.is_error
        assert "No files found" in result.content
        assert result.details["count"] == 0

    @pytest.mark.asyncio
    async def test_missing_pattern(self, temp_dir):
        """Test error when pattern is missing."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test8",
            arguments={}
        )

        assert result.is_error
        assert "pattern parameter is required" in result.content

    @pytest.mark.asyncio
    async def test_nonexistent_directory(self, temp_dir):
        """Test error when specified directory doesn't exist."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test9",
            arguments={
                "pattern": "*.py",
                "path": "/nonexistent/directory"
            }
        )

        assert result.is_error
        assert "does not exist" in result.content

    @pytest.mark.asyncio
    async def test_wildcard_pattern(self, temp_dir):
        """Test wildcard pattern matching."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test10",
            arguments={"pattern": "file*"}
        )

        assert not result.is_error
        assert "file1.py" in result.content
        assert "file2.py" in result.content

    @pytest.mark.asyncio
    async def test_question_mark_pattern(self, temp_dir):
        """Test single character wildcard (?)."""
        tool = GlobTool(working_dir=temp_dir)

        # Create files for this test
        (temp_dir / "a1.txt").touch()
        (temp_dir / "a2.txt").touch()
        (temp_dir / "b1.txt").touch()

        result = await tool.execute(
            tool_call_id="test11",
            arguments={"pattern": "a?.txt"}
        )

        assert not result.is_error
        assert "a1.txt" in result.content
        assert "a2.txt" in result.content
        assert "b1.txt" not in result.content

    @pytest.mark.asyncio
    async def test_character_class_pattern(self, temp_dir):
        """Test character class pattern [abc]."""
        tool = GlobTool(working_dir=temp_dir)

        # Create test files
        (temp_dir / "data_a.txt").touch()
        (temp_dir / "data_b.txt").touch()
        (temp_dir / "data_c.txt").touch()
        (temp_dir / "data_d.txt").touch()

        result = await tool.execute(
            tool_call_id="test12",
            arguments={"pattern": "data_[abc].txt"}
        )

        assert not result.is_error
        assert "data_a.txt" in result.content
        assert "data_b.txt" in result.content
        assert "data_c.txt" in result.content
        assert "data_d.txt" not in result.content

    @pytest.mark.asyncio
    async def test_large_result_set(self, temp_dir):
        """Test handling of large result sets (>100 files)."""
        tool = GlobTool(working_dir=temp_dir)

        # Create many files
        many_dir = temp_dir / "many"
        many_dir.mkdir()
        for i in range(150):
            (many_dir / f"file_{i:03d}.txt").touch()

        result = await tool.execute(
            tool_call_id="test13",
            arguments={"pattern": "many/*.txt"}
        )

        assert not result.is_error
        assert result.details["count"] == 150
        assert "and 50 more" in result.content  # Shows truncation

    @pytest.mark.asyncio
    async def test_details_metadata(self, temp_dir):
        """Test that result includes proper metadata."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test14",
            arguments={"pattern": "*.py"}
        )

        assert not result.is_error
        assert "pattern" in result.details
        assert "base_dir" in result.details
        assert "count" in result.details
        assert "files" in result.details
        assert result.details["pattern"] == "*.py"
        assert isinstance(result.details["files"], list)

    @pytest.mark.asyncio
    async def test_on_update_callback(self, temp_dir):
        """Test that on_update callback is called."""
        tool = GlobTool(working_dir=temp_dir)
        updates = []

        def on_update(msg):
            updates.append(msg)

        result = await tool.execute(
            tool_call_id="test15",
            arguments={"pattern": "*.py"},
            on_update=on_update
        )

        assert not result.is_error
        assert len(updates) > 0
        assert "Searching" in updates[0]

    @pytest.mark.asyncio
    async def test_relative_paths(self, temp_dir):
        """Test that results use relative paths when possible."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test16",
            arguments={"pattern": "**/*.py"}
        )

        assert not result.is_error
        # Results should use relative paths, not absolute
        for file_path in result.details["files"]:
            assert not file_path.startswith("/")

    @pytest.mark.asyncio
    async def test_sorted_results(self, temp_dir):
        """Test that results are sorted."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test17",
            arguments={"pattern": "*.py"}
        )

        assert not result.is_error
        files = result.details["files"]
        assert files == sorted(files)

    @pytest.mark.asyncio
    async def test_yaml_config_files(self, temp_dir):
        """Test finding YAML config files."""
        tool = GlobTool(working_dir=temp_dir)

        result = await tool.execute(
            tool_call_id="test18",
            arguments={"pattern": "**/*.yaml"}
        )

        assert not result.is_error
        assert "config.yaml" in result.content

    @pytest.mark.asyncio
    async def test_multiple_extensions(self, temp_dir):
        """Test pattern matching multiple file types."""
        tool = GlobTool(working_dir=temp_dir)

        # Test with multiple patterns would require multiple calls
        result_py = await tool.execute(
            tool_call_id="test19a",
            arguments={"pattern": "**/*.py"}
        )

        result_js = await tool.execute(
            tool_call_id="test19b",
            arguments={"pattern": "**/*.js"}
        )

        assert not result_py.is_error
        assert not result_js.is_error
        assert result_py.details["count"] > 0
        assert result_js.details["count"] > 0


class TestGlobToolEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_directory(self):
        """Test glob in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = GlobTool(working_dir=Path(tmpdir))

            result = await tool.execute(
                tool_call_id="edge1",
                arguments={"pattern": "*.py"}
            )

            assert not result.is_error
            assert "No files found" in result.content

    @pytest.mark.asyncio
    async def test_special_characters_in_pattern(self):
        """Test handling special characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create files with special names
            (tmp_path / "test_file.py").touch()
            (tmp_path / "test-file.py").touch()

            tool = GlobTool(working_dir=tmp_path)

            result = await tool.execute(
                tool_call_id="edge2",
                arguments={"pattern": "test_*.py"}
            )

            assert not result.is_error
            assert "test_file.py" in result.content

    @pytest.mark.asyncio
    async def test_default_base_dir(self):
        """Test tool with default base directory."""
        tool = GlobTool()  # Should use current directory

        # Just verify it doesn't crash
        result = await tool.execute(
            tool_call_id="edge3",
            arguments={"pattern": "*.py"}
        )

        # May or may not find files, but shouldn't error
        assert isinstance(result.is_error, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
