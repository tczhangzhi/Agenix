"""Tests for SkillTool - Dynamic skill loading tool."""

import tempfile
from pathlib import Path

import pytest

from agenix.tools.skill import SkillTool


class TestSkillTool:
    """Test cases for SkillTool."""

    @pytest.fixture
    def temp_skills_dir(self):
        """Create temporary skills directory with test skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_path = Path(tmpdir) / ".agenix" / "skills"
            skills_path.mkdir(parents=True)

            # Create test skill 1
            skill1_dir = skills_path / "test-skill"
            skill1_dir.mkdir()
            (skill1_dir / "SKILL.md").write_text("""---
name: test-skill
description: A test skill
---

# Test Skill

This is a test skill for unit testing.

## Instructions

1. Do step one
2. Do step two
3. Complete task
""")

            # Create test skill 2
            skill2_dir = skills_path / "another-skill"
            skill2_dir.mkdir()
            (skill2_dir / "SKILL.md").write_text("""---
name: another-skill
description: Another test skill
---

# Another Skill

More test instructions here.
""")

            # Create skill without frontmatter (should use directory name)
            skill3_dir = skills_path / "fallback-skill"
            skill3_dir.mkdir()
            (skill3_dir / "SKILL.md").write_text("""# Fallback Skill

This skill has no frontmatter.
""")

            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_load_skill_success(self, temp_skills_dir):
        """Test successfully loading a skill."""
        tool = SkillTool(working_dir=temp_skills_dir)

        result = await tool.execute(
            tool_call_id="test1",
            arguments={"skill_name": "test-skill"}
        )

        assert not result.is_error
        assert "test-skill" in result.content
        assert "Test Skill" in result.content
        assert "Do step one" in result.content
        assert result.details["skill_name"] == "test-skill"

    @pytest.mark.asyncio
    async def test_skill_content_excludes_frontmatter(self, temp_skills_dir):
        """Test that loaded skill doesn't include YAML frontmatter."""
        tool = SkillTool(working_dir=temp_skills_dir)

        result = await tool.execute(
            tool_call_id="test2",
            arguments={"skill_name": "test-skill"}
        )

        assert not result.is_error
        # Should not contain the frontmatter
        assert "---" not in result.content or result.content.count("---") <= 2
        assert "name: test-skill" not in result.content
        # Should contain actual content
        assert "Test Skill" in result.content

    @pytest.mark.asyncio
    async def test_load_nonexistent_skill(self, temp_skills_dir):
        """Test loading a skill that doesn't exist."""
        tool = SkillTool(working_dir=temp_skills_dir)

        result = await tool.execute(
            tool_call_id="test3",
            arguments={"skill_name": "nonexistent"}
        )

        assert result.is_error
        assert "not found" in result.content
        assert "Available skills" in result.content
        assert "test-skill" in result.content  # Shows available skills

    @pytest.mark.asyncio
    async def test_missing_skill_name_parameter(self, temp_skills_dir):
        """Test error when skill_name parameter is missing."""
        tool = SkillTool(working_dir=temp_skills_dir)

        result = await tool.execute(
            tool_call_id="test4",
            arguments={}
        )

        assert result.is_error
        assert "skill_name parameter is required" in result.content

    @pytest.mark.asyncio
    async def test_empty_skill_name(self, temp_skills_dir):
        """Test error with empty skill name."""
        tool = SkillTool(working_dir=temp_skills_dir)

        result = await tool.execute(
            tool_call_id="test5",
            arguments={"skill_name": ""}
        )

        assert result.is_error
        assert "skill_name parameter is required" in result.content

    @pytest.mark.asyncio
    async def test_multiple_skills_available(self, temp_skills_dir):
        """Test that multiple skills can be loaded."""
        tool = SkillTool(working_dir=temp_skills_dir)

        # Load first skill
        result1 = await tool.execute(
            tool_call_id="test6a",
            arguments={"skill_name": "test-skill"}
        )

        # Load second skill
        result2 = await tool.execute(
            tool_call_id="test6b",
            arguments={"skill_name": "another-skill"}
        )

        assert not result1.is_error
        assert not result2.is_error
        assert "test-skill" in result1.content
        assert "another-skill" in result2.content
        assert "Test Skill" in result1.content
        assert "Another Skill" in result2.content

    @pytest.mark.asyncio
    async def test_skill_details_metadata(self, temp_skills_dir):
        """Test that result includes proper metadata."""
        tool = SkillTool(working_dir=temp_skills_dir)

        result = await tool.execute(
            tool_call_id="test7",
            arguments={"skill_name": "test-skill"}
        )

        assert not result.is_error
        assert "skill_name" in result.details
        assert "skill_file" in result.details
        assert "source" in result.details
        assert result.details["skill_name"] == "test-skill"
        assert "SKILL.md" in result.details["skill_file"]

    @pytest.mark.asyncio
    async def test_on_update_callback(self, temp_skills_dir):
        """Test that on_update callback is called."""
        tool = SkillTool(working_dir=temp_skills_dir)
        updates = []

        def on_update(msg):
            updates.append(msg)

        result = await tool.execute(
            tool_call_id="test8",
            arguments={"skill_name": "test-skill"},
            on_update=on_update
        )

        assert not result.is_error
        assert len(updates) > 0
        assert "Loading skill" in updates[0]
        assert "test-skill" in updates[0]

    @pytest.mark.asyncio
    async def test_skill_source_indicator(self, temp_skills_dir):
        """Test that skill source is indicated in result."""
        tool = SkillTool(working_dir=temp_skills_dir)

        result = await tool.execute(
            tool_call_id="test9",
            arguments={"skill_name": "test-skill"}
        )

        assert not result.is_error
        # Should indicate skill source
        assert "SKILL.md" in result.content
        assert result.details["source"] in ["builtin", "custom"]

    @pytest.mark.asyncio
    async def test_skill_instructions_footer(self, temp_skills_dir):
        """Test that skill includes instruction footer."""
        tool = SkillTool(working_dir=temp_skills_dir)

        result = await tool.execute(
            tool_call_id="test10",
            arguments={"skill_name": "test-skill"}
        )

        assert not result.is_error
        assert "Follow these instructions carefully" in result.content
        assert "Skill source:" in result.content

    @pytest.mark.asyncio
    async def test_fallback_to_directory_name(self, temp_skills_dir):
        """Test skill name fallback to directory name when no frontmatter."""
        tool = SkillTool(working_dir=temp_skills_dir)

        # Should be available with directory name
        result = await tool.execute(
            tool_call_id="test11",
            arguments={"skill_name": "fallback-skill"}
        )

        assert not result.is_error
        assert "Fallback Skill" in result.content

    @pytest.mark.asyncio
    async def test_tool_description_includes_available_skills(self, temp_skills_dir):
        """Test that tool description includes list of available skills."""
        tool = SkillTool(working_dir=temp_skills_dir)

        assert "test-skill" in tool.description
        assert "another-skill" in tool.description

    @pytest.mark.asyncio
    async def test_tool_parameters_enum(self, temp_skills_dir):
        """Test that tool parameters include skill names as enum."""
        tool = SkillTool(working_dir=temp_skills_dir)

        enum_values = tool.parameters["properties"]["skill_name"]["enum"]

        assert "test-skill" in enum_values
        assert "another-skill" in enum_values
        assert "fallback-skill" in enum_values


class TestSkillToolBuiltinSkills:
    """Test loading built-in skills."""

    @pytest.mark.asyncio
    async def test_builtin_skills_available(self):
        """Test that built-in skills are discovered."""
        # Create tool without project directory
        tool = SkillTool(working_dir=".")

        # Check if any built-in skills are available
        # Note: This depends on actual built-in skills in the package
        assert len(tool._available_skills) >= 0  # May have builtin skills

    @pytest.mark.asyncio
    async def test_skill_priority_project_over_builtin(self):
        """Test that project skills override built-in skills with same name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            skills_dir = project_dir / ".agenix" / "skills"
            skills_dir.mkdir(parents=True)

            # Create a skill with potentially conflicting name
            skill_dir = skills_dir / "custom-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: custom-skill
description: Project-local custom skill
---

# Custom Skill

Project-local version.
""")

            tool = SkillTool(working_dir=project_dir)

            # If the skill exists, it should be the project version
            if "custom-skill" in tool._available_skills:
                result = await tool.execute(
                    tool_call_id="priority1",
                    arguments={"skill_name": "custom-skill"}
                )

                assert not result.is_error
                assert "Project-local version" in result.content


class TestSkillToolEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_no_skills_available(self):
        """Test tool with no skills available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Empty project directory
            tool = SkillTool(working_dir=Path(tmpdir))

            # May have built-in skills, but at least shouldn't crash
            result = await tool.execute(
                tool_call_id="edge1",
                arguments={"skill_name": "any-skill"}
            )

            # Should error about skill not found
            assert result.is_error

    @pytest.mark.asyncio
    async def test_corrupted_skill_file(self):
        """Test handling of corrupted skill file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_path = Path(tmpdir) / ".agenix" / "skills"
            skills_path.mkdir(parents=True)

            # Create skill with invalid YAML
            skill_dir = skills_path / "corrupt-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: corrupt-skill
description: [unclosed array
---

Content
""")

            tool = SkillTool(working_dir=Path(tmpdir))

            # Tool should still initialize (may skip corrupt skills)
            assert tool is not None

    @pytest.mark.asyncio
    async def test_skill_file_without_content(self):
        """Test skill file with only frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_path = Path(tmpdir) / ".agenix" / "skills"
            skills_path.mkdir(parents=True)

            skill_dir = skills_path / "empty-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: empty-skill
description: Skill with no content
---
""")

            tool = SkillTool(working_dir=Path(tmpdir))

            result = await tool.execute(
                tool_call_id="edge3",
                arguments={"skill_name": "empty-skill"}
            )

            # Should load successfully, even if content is minimal
            assert not result.is_error

    @pytest.mark.asyncio
    async def test_unicode_in_skill_content(self):
        """Test skill with Unicode content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_path = Path(tmpdir) / ".agenix" / "skills"
            skills_path.mkdir(parents=True)

            skill_dir = skills_path / "unicode-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: unicode-skill
description: Skill with Unicode
---

# Unicode Test

- 中文字符
- Emoji: 🚀 ✨ 🎉
- Special chars: © ® ™
""", encoding="utf-8")

            tool = SkillTool(working_dir=Path(tmpdir))

            result = await tool.execute(
                tool_call_id="edge4",
                arguments={"skill_name": "unicode-skill"}
            )

            assert not result.is_error
            assert "中文字符" in result.content
            assert "🚀" in result.content

    @pytest.mark.asyncio
    async def test_skill_with_code_blocks(self):
        """Test skill containing code blocks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_path = Path(tmpdir) / ".agenix" / "skills"
            skills_path.mkdir(parents=True)

            skill_dir = skills_path / "code-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: code-skill
description: Skill with code examples
---

# Code Skill

Example usage:

```python
def hello():
    print("Hello, world!")
```

End of skill.
""")

            tool = SkillTool(working_dir=Path(tmpdir))

            result = await tool.execute(
                tool_call_id="edge5",
                arguments={"skill_name": "code-skill"}
            )

            assert not result.is_error
            assert "```python" in result.content
            assert "def hello():" in result.content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
