"""Test suite for core.skills module.

This module contains comprehensive unit tests for the Skills management system,
following the Anthropic Agent Skills standard.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from agenix.core.skills import Skill, SkillManager


class TestSkill:
    """Test cases for Skill dataclass."""

    def test_create_basic_skill(self):
        """Test creating a basic skill with required fields only."""
        skill = Skill(
            name="test-skill",
            description="A test skill",
            file_path="/path/to/skill.md",
            content="# Test Skill\n\nContent here"
        )

        assert skill.name == "test-skill"
        assert skill.description == "A test skill"
        assert skill.file_path == "/path/to/skill.md"
        assert "Test Skill" in skill.content
        assert skill.disable_model_invocation is False
        assert skill.metadata == {}

    def test_skill_with_all_fields(self):
        """Test creating skill with all optional fields."""
        skill = Skill(
            name="test-skill",
            description="A test skill",
            file_path="/path/to/skill.md",
            content="Content",
            license="MIT",
            compatibility="Python 3.8+",
            allowed_tools=["Bash(test:*)", "Read"],
            metadata={"author": "Test Author", "version": "1.0"},
            disable_model_invocation=True
        )

        assert skill.license == "MIT"
        assert skill.compatibility == "Python 3.8+"
        assert skill.allowed_tools == ["Bash(test:*)", "Read"]
        assert skill.metadata["author"] == "Test Author"
        assert skill.metadata["version"] == "1.0"
        assert skill.disable_model_invocation is True

    def test_skill_with_allowed_tools_list(self):
        """Test skill with multiple allowed tools."""
        skill = Skill(
            name="browser",
            description="Browser automation",
            file_path="/path/to/skill.md",
            content="Content",
            allowed_tools=["Bash(browser:*)", "Read", "Write"]
        )

        assert len(skill.allowed_tools) == 3
        assert "Bash(browser:*)" in skill.allowed_tools
        assert "Read" in skill.allowed_tools


class TestSkillManager:
    """Test cases for SkillManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.temp_dir) / "skills"
        self.skills_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)

    def create_test_skill(self, name, description="Test skill", **kwargs):
        """Helper to create a test skill file with optional fields.

        Args:
            name: Skill name
            description: Skill description
            **kwargs: Additional frontmatter fields (license, allowed-tools, etc.)
        """
        # Build frontmatter
        frontmatter_dict = {
            'name': name,
            'description': description
        }
        frontmatter_dict.update(kwargs)

        # Convert to YAML
        import yaml
        frontmatter_yaml = yaml.dump(
            frontmatter_dict, default_flow_style=False)

        content = f"""---
{frontmatter_yaml}---

# {name.title()} Skill

Test content
"""
        skill_file = self.skills_dir / f"{name}.md"
        skill_file.write_text(content)
        return skill_file

    def test_skill_manager_init(self):
        """Test creating a skill manager."""
        self.setUp()
        try:
            manager = SkillManager(skill_dirs=[str(self.skills_dir)])

            assert manager is not None
            assert len(manager.skill_dirs) >= 1
        finally:
            self.tearDown()

    def test_discover_direct_md_files(self):
        """Test discovering direct .md files in skills directory."""
        self.setUp()
        try:
            # Create test skill
            self.create_test_skill("test-skill")

            manager = SkillManager(skill_dirs=[str(self.skills_dir)])

            assert len(manager.skills) == 1
            assert "test-skill" in manager.skills
        finally:
            self.tearDown()

    def test_discover_skill_md_in_subdirectory(self):
        """Test discovering SKILL.md files in subdirectories."""
        self.setUp()
        try:
            # Create subdirectory with SKILL.md
            skill_subdir = self.skills_dir / "my-skill"
            skill_subdir.mkdir()

            content = """---
name: my-skill
description: A subdirectory skill
---

# My Skill
"""
            (skill_subdir / "SKILL.md").write_text(content)

            manager = SkillManager(skill_dirs=[str(self.skills_dir)])

            assert len(manager.skills) == 1
            assert "my-skill" in manager.skills
        finally:
            self.tearDown()

    def test_validate_skill_name(self):
        """Test skill name validation."""
        manager = SkillManager(skill_dirs=[])

        # Valid names
        assert manager._validate_name("test-skill") is True
        assert manager._validate_name("skill123") is True
        assert manager._validate_name("a") is True

        # Invalid names
        assert manager._validate_name("Test-Skill") is False  # Uppercase
        assert manager._validate_name("-test") is False  # Leading hyphen
        assert manager._validate_name("test-") is False  # Trailing hyphen
        assert manager._validate_name(
            "test--skill") is False  # Consecutive hyphens
        assert manager._validate_name("") is False  # Empty
        assert manager._validate_name("a" * 65) is False  # Too long

    def test_get_skill(self):
        """Test retrieving a skill by name."""
        self.setUp()
        try:
            self.create_test_skill("test-skill")

            manager = SkillManager(skill_dirs=[str(self.skills_dir)])
            skill = manager.get_skill("test-skill")

            assert skill is not None
            assert skill.name == "test-skill"
        finally:
            self.tearDown()

    def test_list_skills(self):
        """Test listing all skills."""
        self.setUp()
        try:
            self.create_test_skill("skill1")
            self.create_test_skill("skill2")

            manager = SkillManager(skill_dirs=[str(self.skills_dir)])
            skills = manager.list_skills()

            assert len(skills) == 2
            skill_names = [s.name for s in skills]
            assert "skill1" in skill_names
            assert "skill2" in skill_names
        finally:
            self.tearDown()

    def test_get_skills_summary(self):
        """Test generating skills summary for system prompt."""
        self.setUp()
        try:
            self.create_test_skill("test-skill", "A test skill for testing")

            manager = SkillManager(skill_dirs=[str(self.skills_dir)])
            summary = manager.get_skills_summary()

            assert "<available_skills>" in summary
            assert 'name="test-skill"' in summary
            assert "A test skill for testing" in summary
            assert "</available_skills>" in summary
        finally:
            self.tearDown()

    def test_disabled_skill_not_in_summary(self):
        """Test that disabled skills don't appear in summary."""
        self.setUp()
        try:
            # Create skill with disable-model-invocation
            content = """---
name: hidden-skill
description: A hidden skill
disable-model-invocation: true
---

# Hidden Skill
"""
            (self.skills_dir / "hidden-skill.md").write_text(content)

            manager = SkillManager(skill_dirs=[str(self.skills_dir)])
            summary = manager.get_skills_summary()

            # Summary should be empty or not contain the hidden skill
            assert "hidden-skill" not in summary
        finally:
            self.tearDown()

    def test_load_skill_content(self):
        """Test loading full skill content."""
        self.setUp()
        try:
            self.create_test_skill("test-skill")

            manager = SkillManager(skill_dirs=[str(self.skills_dir)])
            content = manager.load_skill_content("test-skill")

            assert content is not None
            assert "Test-Skill Skill" in content or "test-skill" in content
        finally:
            self.tearDown()

    def test_name_collision_warning(self):
        """Test that name collisions are detected."""
        self.setUp()
        try:
            # Create two skills with same name in different locations
            self.create_test_skill("duplicate")

            # Create second directory
            skills_dir2 = Path(self.temp_dir) / "skills2"
            skills_dir2.mkdir()

            content = """---
name: duplicate
description: Another duplicate
---

# Duplicate
"""
            (skills_dir2 / "duplicate.md").write_text(content)

            # Load from both directories
            manager = SkillManager(
                skill_dirs=[str(self.skills_dir), str(skills_dir2)])

            # Should only have one skill (first one found)
            assert len(manager.skills) == 1
            assert "duplicate" in manager.skills
        finally:
            self.tearDown()

    def test_add_skill_dir(self):
        """Test adding a skill directory dynamically."""
        self.setUp()
        try:
            self.create_test_skill("skill1")

            # Create manager with first directory
            manager = SkillManager(skill_dirs=[str(self.skills_dir)])
            assert len(manager.skills) == 1

            # Create second directory with another skill
            skills_dir2 = Path(self.temp_dir) / "skills2"
            skills_dir2.mkdir()

            content = """---
name: skill2
description: Second skill
---

# Skill 2
"""
            (skills_dir2 / "skill2.md").write_text(content)

            # Add second directory
            manager.add_skill_dir(str(skills_dir2))

            assert len(manager.skills) == 2
            assert "skill2" in manager.skills
        finally:
            self.tearDown()

    def test_skill_with_allowed_tools_string(self):
        """Test parsing allowed-tools as a single string."""
        self.setUp()
        try:
            content = """---
name: browser
description: Browser automation
allowed-tools: Bash(browser:*)
---

# Browser Skill
"""
            (self.skills_dir / "browser.md").write_text(content)

            manager = SkillManager(skill_dirs=[str(self.skills_dir)])
            skill = manager.get_skill("browser")

            assert skill is not None
            assert skill.allowed_tools == ["Bash(browser:*)"]
        finally:
            self.tearDown()

    def test_skill_with_allowed_tools_list(self):
        """Test parsing allowed-tools as a list."""
        self.setUp()
        try:
            self.create_test_skill(
                "multi-tool",
                description="Multi-tool skill",
                **{"allowed-tools": ["Bash(tool:*)", "Read", "Write"]}
            )

            manager = SkillManager(skill_dirs=[str(self.skills_dir)])
            skill = manager.get_skill("multi-tool")

            assert skill is not None
            assert len(skill.allowed_tools) == 3
            assert "Bash(tool:*)" in skill.allowed_tools
            assert "Read" in skill.allowed_tools
            assert "Write" in skill.allowed_tools
        finally:
            self.tearDown()

    def test_skill_with_all_optional_fields(self):
        """Test skill with all optional Anthropic spec fields."""
        self.setUp()
        try:
            self.create_test_skill(
                "full-skill",
                description="Complete skill with all fields",
                license="MIT",
                compatibility="Python 3.8+",
                **{
                    "allowed-tools": ["Bash(full:*)", "Read"],
                    "disable-model-invocation": True,
                    "metadata": {"author": "Test", "version": "1.0"}
                }
            )

            manager = SkillManager(skill_dirs=[str(self.skills_dir)])
            skill = manager.get_skill("full-skill")

            assert skill is not None
            assert skill.license == "MIT"
            assert skill.compatibility == "Python 3.8+"
            assert skill.allowed_tools == ["Bash(full:*)", "Read"]
            assert skill.disable_model_invocation is True
            assert skill.metadata["author"] == "Test"
            assert skill.metadata["version"] == "1.0"
        finally:
            self.tearDown()

    def test_parse_frontmatter_with_allowed_tools(self):
        """Test frontmatter parsing with allowed-tools field."""
        manager = SkillManager(skill_dirs=[])

        content = """---
name: test
description: Test skill
allowed-tools:
  - Bash(test:*)
  - Read
---

# Content
"""
        frontmatter = manager._parse_frontmatter(content)

        assert frontmatter is not None
        assert "allowed-tools" in frontmatter
        assert isinstance(frontmatter["allowed-tools"], list)
        assert len(frontmatter["allowed-tools"]) == 2


class TestDefaultSkills:
    """Test cases for loading bundled default skills."""

    def test_load_pdf_skill(self):
        """Test loading the pdf skill from default-skills."""
        # Use default-skills directory (bundled with package)
        default_skills_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "agenix", "default-skills")

        manager = SkillManager(skill_dirs=[default_skills_dir])
        skill = manager.get_skill("pdf")

        assert skill is not None
        assert skill.name == "pdf"
        assert "PDF" in skill.description or "pdf" in skill.description
        assert skill.license is not None
        assert "SKILL.md" in skill.file_path
        assert "default-skills" in skill.file_path

    def test_load_xlsx_skill(self):
        """Test loading the xlsx skill from default-skills."""
        default_skills_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "agenix", "default-skills")

        manager = SkillManager(skill_dirs=[default_skills_dir])
        skill = manager.get_skill("xlsx")

        assert skill is not None
        assert skill.name == "xlsx"
        assert "spreadsheet" in skill.description.lower(
        ) or "xlsx" in skill.description.lower()
        assert skill.license is not None
        assert "default-skills" in skill.file_path

    def test_load_browser_use_skill(self):
        """Test loading the browser-use skill with allowed-tools."""
        default_skills_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "agenix", "default-skills")

        manager = SkillManager(skill_dirs=[default_skills_dir])
        skill = manager.get_skill("browser-use")

        assert skill is not None
        assert skill.name == "browser-use"
        assert "browser" in skill.description.lower()
        # Check that allowed-tools is parsed
        assert skill.allowed_tools is not None
        assert len(skill.allowed_tools) > 0
        assert any("browser" in tool.lower() for tool in skill.allowed_tools)
        assert "default-skills" in skill.file_path

    def test_load_all_default_skills(self):
        """Test loading all default skills."""
        default_skills_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "agenix", "default-skills")

        manager = SkillManager(skill_dirs=[default_skills_dir])
        skills = manager.list_skills()

        # Should have the 7 default skills
        assert len(skills) >= 7

        # Check that all skills have required fields
        for skill in skills:
            assert skill.name
            assert skill.description
            assert skill.file_path
            assert skill.content
            assert len(skill.name) <= 64
            assert skill.name.islower() or '-' in skill.name
            assert "default-skills" in skill.file_path

        # Check for expected default skills
        skill_names = {skill.name for skill in skills}
        expected_skills = {"pdf", "xlsx", "docx", "pptx", "browser-use", "find-skills", "skill-creator"}
        assert expected_skills.issubset(skill_names), f"Missing skills: {expected_skills - skill_names}"

    def test_skills_summary_excludes_disabled(self):
        """Test that skills summary excludes disabled skills."""
        default_skills_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "agenix", "default-skills")

        manager = SkillManager(skill_dirs=[default_skills_dir])
        summary = manager.get_skills_summary()

        # Summary should have available_skills tag
        assert "<available_skills>" in summary
        assert "</available_skills>" in summary

        # Check that visible skills are included
        for skill in manager.list_skills():
            if not skill.disable_model_invocation:
                assert f'name="{skill.name}"' in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
