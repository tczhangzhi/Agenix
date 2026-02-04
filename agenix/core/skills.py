"""Skill management system following the Anthropic Agent Skills standard.

This module implements the Agent Skills specification, providing discovery,
loading, and management of skills that extend Claude's capabilities.

Skills are defined using markdown files with YAML frontmatter containing:
- name (required): Unique identifier (lowercase, hyphens, 1-64 chars)
- description (required): Brief description of what the skill does
- license (optional): License terms for the skill
- compatibility (optional): Compatibility requirements
- allowed-tools (optional): List of tools the skill can use
- disable-model-invocation (optional): If true, skill is not shown to model
- metadata (optional): Additional custom metadata

Examples:
    >>> manager = SkillManager(skill_dirs=['/path/to/skills'])
    >>> skill = manager.get_skill('pdf')
    >>> print(skill.description)
    'PDF manipulation toolkit...'
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class Skill:
    """Represents a skill with its metadata and content.

    A skill extends Claude's capabilities by providing specialized knowledge
    or workflows. Skills follow the Anthropic Agent Skills standard.

    Attributes:
        name (str): Unique skill identifier (lowercase, hyphens, 1-64 chars)
        description (str): Brief description of the skill's purpose
        file_path (str): Absolute path to the skill's markdown file
        content (str): Full markdown content including frontmatter
        license (Optional[str]): License terms for the skill
        compatibility (Optional[str]): Compatibility requirements (e.g., "Python 3.8+")
        allowed_tools (Optional[List[str]]): List of tools this skill can use
        metadata (Dict[str, Any]): Additional custom metadata
        disable_model_invocation (bool): If True, skill is not shown to model

    Examples:
        >>> skill = Skill(
        ...     name="pdf",
        ...     description="PDF manipulation toolkit",
        ...     file_path="/skills/pdf/SKILL.md",
        ...     content="---\\nname: pdf\\n...",
        ...     allowed_tools=["Bash(pdf:*)"]
        ... )
        >>> print(skill.name)
        'pdf'
    """
    name: str
    description: str
    file_path: str
    content: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    allowed_tools: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    disable_model_invocation: bool = False


class SkillManager:
    """Manages discovery, loading, and access to skills.

    The SkillManager discovers skills from configured directories, parses
    their frontmatter, validates them according to the Agent Skills standard,
    and provides access to skill metadata and content.

    Skill discovery looks for:
    - Direct .md files in the root of skill directories
    - SKILL.md files in subdirectories (subdirectory name should match skill name)

    Default skill directories (if no custom dirs specified):
    - Global: ~/.agenix/skills/
    - Project: .agenix/skills/

    Attributes:
        skill_dirs (List[str]): List of directories to search for skills
        skills (Dict[str, Skill]): Dictionary mapping skill names to Skill objects

    Examples:
        >>> # Use default directories
        >>> manager = SkillManager()
        >>> print(len(manager.list_skills()))
        5

        >>> # Custom directories
        >>> manager = SkillManager(skill_dirs=['/my/skills', '/other/skills'])
        >>> skill = manager.get_skill('pdf')
        >>> content = manager.load_skill_content('pdf')

        >>> # Generate summary for system prompt
        >>> summary = manager.get_skills_summary()
        >>> print(summary)
        <available_skills>
          <skill name="pdf">
            PDF manipulation toolkit...
          </skill>
        </available_skills>
    """

    def __init__(self, skill_dirs: Optional[List[str]] = None):
        """Initialize skill manager and load skills.

        Args:
            skill_dirs: List of directories to search for skills. If None,
                uses default directories (~/.agenix/skills/ and .agenix/skills/)

        Examples:
            >>> manager = SkillManager()  # Use defaults
            >>> manager = SkillManager(skill_dirs=['/custom/path'])  # Custom
        """
        self.skill_dirs = skill_dirs or self._default_skill_dirs()
        self.skills: Dict[str, Skill] = {}
        self._load_skills()

    def _default_skill_dirs(self) -> List[str]:
        """Get default skill directories.

        Returns:
            List of existing default skill directories in priority order:
            1. Global: ~/.agenix/skills/
            2. Project: .agenix/skills/

        Note:
            Only returns directories that actually exist on the filesystem.
        """
        dirs = []

        # Global: ~/.agenix/skills/
        home = Path.home()
        global_dir = home / ".agenix" / "skills"
        if global_dir.exists():
            dirs.append(str(global_dir))

        # Project: .agenix/skills/
        project_dir = Path(".agenix/skills")
        if project_dir.exists():
            dirs.append(str(project_dir))

        return dirs

    def _load_skills(self):
        """Load all skills from configured directories.

        Iterates through each skill directory and discovers all skills.
        Later directories can override skills from earlier directories
        (e.g., user skills override default skills, project skills override both).
        """
        for skill_dir in self.skill_dirs:
            self._discover_skills(skill_dir)

    def _discover_skills(self, directory: str):
        """Discover skills in a directory.

        Looks for two patterns:
        1. Direct .md files in the root directory
        2. SKILL.md files in subdirectories

        Args:
            directory: Path to directory to search for skills

        Note:
            For SKILL.md files in subdirectories, a warning is issued if the
            skill name doesn't match the parent directory name.
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            return

        # Direct .md files in root
        for md_file in dir_path.glob("*.md"):
            skill = self._load_skill_file(md_file)
            if skill:
                self._register_skill(skill)

        # SKILL.md files in subdirectories
        for skill_file in dir_path.rglob("SKILL.md"):
            skill = self._load_skill_file(skill_file)
            if skill:
                self._register_skill(skill)

    def _load_skill_file(self, file_path: Path) -> Optional[Skill]:
        """Load a skill from a markdown file.

        Parses the YAML frontmatter, validates required fields (name and
        description), and validates the skill name according to the spec.

        Args:
            file_path: Path to the skill markdown file

        Returns:
            Skill object if valid, None if invalid or parsing fails

        Note:
            Prints warnings for invalid skills but continues execution.
            This allows the system to load valid skills even if some are malformed.

        Examples:
            Valid skill file:
            ```markdown
            ---
            name: pdf
            description: PDF manipulation toolkit
            allowed-tools:
              - Bash(pdf:*)
            ---

            # PDF Processing
            ...
            ```
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter
            frontmatter = self._parse_frontmatter(content)
            if not frontmatter:
                return None

            # Validate required fields
            name = frontmatter.get('name')
            description = frontmatter.get('description')

            if not name or not description:
                print(
                    f"Warning: Skill at {file_path} missing required fields (name or description)")
                return None

            # Validate name
            if not self._validate_name(name):
                print(
                    f"Warning: Skill at {file_path} has invalid name: {name}")
                return None

            # Check if name matches parent directory (for SKILL.md files)
            if file_path.name == "SKILL.md":
                parent_name = file_path.parent.name
                if name != parent_name:
                    print(
                        f"Warning: Skill name '{name}' doesn't match parent directory '{parent_name}'")

            # Parse allowed-tools (can be string or list)
            allowed_tools = frontmatter.get('allowed-tools')
            if allowed_tools is not None:
                if isinstance(allowed_tools, str):
                    allowed_tools = [allowed_tools]
                elif not isinstance(allowed_tools, list):
                    print(
                        f"Warning: Skill at {file_path} has invalid allowed-tools format")
                    allowed_tools = None

            # Create skill object
            skill = Skill(
                name=name,
                description=description,
                file_path=str(file_path),
                content=content,
                license=frontmatter.get('license'),
                compatibility=frontmatter.get('compatibility'),
                allowed_tools=allowed_tools,
                metadata=frontmatter.get('metadata', {}),
                disable_model_invocation=frontmatter.get(
                    'disable-model-invocation', False)
            )

            return skill

        except Exception as e:
            print(f"Error loading skill from {file_path}: {e}")
            return None

    def _parse_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse YAML frontmatter from markdown content.

        Frontmatter must be delimited by --- lines at the start of the file.

        Args:
            content: Markdown content with frontmatter

        Returns:
            Parsed frontmatter dictionary, or None if parsing fails or
            frontmatter is missing

        Examples:
            >>> content = '''---
            ... name: pdf
            ... description: PDF toolkit
            ... ---
            ... # Content
            ... '''
            >>> manager = SkillManager(skill_dirs=[])
            >>> result = manager._parse_frontmatter(content)
            >>> print(result['name'])
            'pdf'
        """
        # Match frontmatter between --- delimiters
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None

        try:
            frontmatter = yaml.safe_load(match.group(1))
            return frontmatter or {}
        except yaml.YAMLError as e:
            print(f"Error parsing frontmatter: {e}")
            return None

    def _validate_name(self, name: str) -> bool:
        """Validate skill name according to Agent Skills standard.

        Rules:
        - 1-64 characters long
        - Lowercase letters, numbers, and hyphens only
        - No leading or trailing hyphens
        - No consecutive hyphens

        Args:
            name: Skill name to validate

        Returns:
            True if valid, False otherwise

        Examples:
            >>> manager = SkillManager(skill_dirs=[])
            >>> manager._validate_name("pdf")
            True
            >>> manager._validate_name("my-skill-123")
            True
            >>> manager._validate_name("Invalid-Name")
            False
            >>> manager._validate_name("-invalid")
            False
        """
        # 1-64 characters
        if not (1 <= len(name) <= 64):
            return False

        # Lowercase letters, numbers, hyphens only
        if not re.match(r'^[a-z0-9-]+$', name):
            return False

        # No leading/trailing hyphens
        if name.startswith('-') or name.endswith('-'):
            return False

        # No consecutive hyphens
        if '--' in name:
            return False

        return True

    def _register_skill(self, skill: Skill):
        """Register a skill in the manager.

        If a skill with the same name already exists, it will be overridden
        by the new skill. This allows later skill directories (user, project)
        to override earlier ones (default).

        Args:
            skill: Skill to register

        Note:
            Later skill directories override earlier ones:
            default-skills < ~/.agenix/skills < .agenix/skills
        """
        if skill.name in self.skills:
            old_path = self.skills[skill.name].file_path
            print(f"Info: Skill '{skill.name}' overridden")
            print(f"  Old: {old_path}")
            print(f"  New: {skill.file_path}")

        self.skills[skill.name] = skill

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name.

        Args:
            name: Skill name

        Returns:
            Skill object if found, None otherwise

        Examples:
            >>> manager = SkillManager(skill_dirs=['/skills'])
            >>> skill = manager.get_skill('pdf')
            >>> if skill:
            ...     print(skill.description)
        """
        return self.skills.get(name)

    def list_skills(self) -> List[Skill]:
        """List all available skills.

        Returns:
            List of all loaded Skill objects

        Examples:
            >>> manager = SkillManager()
            >>> for skill in manager.list_skills():
            ...     print(f"{skill.name}: {skill.description}")
        """
        return list(self.skills.values())

    def get_skills_summary(self) -> str:
        """Get a summary of available skills for system prompt.

        Generates an XML-formatted summary of skills that are not disabled.
        This summary is injected into the system prompt to make Claude aware
        of available skills.

        Returns:
            XML-formatted string with skill names and descriptions, or empty
            string if no visible skills

        Examples:
            >>> manager = SkillManager(skill_dirs=['/skills'])
            >>> summary = manager.get_skills_summary()
            >>> print(summary)
            <available_skills>
              <skill name="pdf">
                PDF manipulation toolkit...
              </skill>
            </available_skills>

        Note:
            Skills with disable_model_invocation=True are excluded from
            the summary. These skills exist but are not shown to the model.
        """
        if not self.skills:
            return ""

        # Filter out skills with disable_model_invocation
        visible_skills = [
            s for s in self.skills.values() if not s.disable_model_invocation]

        if not visible_skills:
            return ""

        lines = ["<available_skills>"]
        for skill in visible_skills:
            lines.append(f"  <skill name=\"{skill.name}\">")
            lines.append(f"    {skill.description}")
            lines.append(f"  </skill>")
        lines.append("</available_skills>")

        return "\n".join(lines)

    def load_skill_content(self, name: str) -> Optional[str]:
        """Load full content of a skill.

        Returns the complete markdown content including frontmatter.
        This is used for progressive disclosure - only loading full skill
        content when the model needs it.

        Args:
            name: Skill name

        Returns:
            Full skill markdown content, or None if skill not found

        Examples:
            >>> manager = SkillManager(skill_dirs=['/skills'])
            >>> content = manager.load_skill_content('pdf')
            >>> if content:
            ...     print("Loaded skill documentation")
        """
        skill = self.get_skill(name)
        if not skill:
            return None

        return skill.content

    def add_skill_dir(self, directory: str):
        """Add a skill directory and load skills from it.

        Dynamically adds a new skill directory to search and discovers
        any skills in that directory.

        Args:
            directory: Path to skill directory

        Examples:
            >>> manager = SkillManager()
            >>> manager.add_skill_dir('/custom/skills')
            >>> print(len(manager.list_skills()))
        """
        if directory not in self.skill_dirs:
            self.skill_dirs.append(directory)
            self._discover_skills(directory)
