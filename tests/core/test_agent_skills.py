"""Tests for Skills integration in Agent."""

import os

import pytest

from agenix.core.agent import Agent, AgentConfig

# Get path to default skills for testing
DEFAULT_SKILLS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "agenix/default-skills"
)


class TestSkillsIntegration:
    """Test Skills system integration with Agent."""

    def test_skills_injected_into_system_prompt(self):
        """Test that skills are properly injected into system prompt."""
        config = AgentConfig(
            api_key="test-key",
            base_url="https://api.example.com/v1",
            model="gpt-4",
            system_prompt="Test prompt.",
            skill_dirs=[DEFAULT_SKILLS_PATH]
        )

        agent = Agent(config)

        # Check that system prompt was modified
        assert config.system_prompt != "Test prompt."
        assert "<available_skills>" in config.system_prompt
        assert "</available_skills>" in config.system_prompt

    def test_skills_usage_instructions_included(self):
        """Test that usage instructions are included."""
        config = AgentConfig(
            api_key="test-key",
            base_url="https://api.example.com/v1",
            model="gpt-4",
            system_prompt="Test.",
            skill_dirs=[DEFAULT_SKILLS_PATH]
        )

        agent = Agent(config)
        prompt = config.system_prompt

        # Check for simple pi-mono style instructions
        assert "The following skills provide specialized instructions" in prompt
        assert "Use the read tool to load a skill's file" in prompt
        assert "When a skill file references a relative path" in prompt

    def test_skill_file_paths_included(self):
        """Test that skill file paths are included in XML format."""
        config = AgentConfig(
            api_key="test-key",
            base_url="https://api.example.com/v1",
            model="gpt-4",
            system_prompt="Test.",
            skill_dirs=[DEFAULT_SKILLS_PATH]
        )

        agent = Agent(config)
        prompt = config.system_prompt

        # Check that skill paths are included in <location> tags
        assert "<location>" in prompt
        assert "</location>" in prompt
        assert "/default-skills/pdf/SKILL.md</location>" in prompt
        assert "/default-skills/browser-use/SKILL.md</location>" in prompt

    def test_xml_format_structure(self):
        """Test that skills use proper XML format."""
        config = AgentConfig(
            api_key="test-key",
            base_url="https://api.example.com/v1",
            model="gpt-4",
            system_prompt="Test.",
            skill_dirs=[DEFAULT_SKILLS_PATH]
        )

        agent = Agent(config)
        prompt = config.system_prompt

        # Check XML structure
        assert "<skill>" in prompt
        assert "</skill>" in prompt
        assert "<name>" in prompt
        assert "</name>" in prompt
        assert "<description>" in prompt
        assert "</description>" in prompt
        assert "<location>" in prompt
        assert "</location>" in prompt

    def test_no_skills_directory(self):
        """Test behavior when no skills directory exists."""
        config = AgentConfig(
            api_key="test-key",
            base_url="https://api.example.com/v1",
            model="gpt-4",
            system_prompt="Test prompt.",
            skill_dirs=["/nonexistent/path"]
        )

        agent = Agent(config)

        # System prompt should not be modified if no skills found
        assert config.system_prompt == "Test prompt."

    def test_skill_manager_loaded(self):
        """Test that SkillManager is properly initialized."""
        config = AgentConfig(
            api_key="test-key",
            base_url="https://api.example.com/v1",
            model="gpt-4",
            skill_dirs=[DEFAULT_SKILLS_PATH]
        )

        agent = Agent(config)

        # Check skill manager exists
        assert agent.skill_manager is not None
        assert len(agent.skill_manager.list_skills()) > 0

        # Check specific skills are loaded
        skill_names = [s.name for s in agent.skill_manager.list_skills()]
        assert "pdf" in skill_names
        assert "browser-use" in skill_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
