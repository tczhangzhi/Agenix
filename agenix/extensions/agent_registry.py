"""Agent Registry - Load and manage agent configurations from AGENT.md files.

This module implements the agent loading system that supports:
- Built-in agents (agenix/agents/)
- User global agents (~/.config/agenix/agents/)
- Project local agents (.agenix/agents/)

Agents are defined using AGENT.md files with YAML frontmatter.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """Agent configuration loaded from AGENT.md.

    This replaces the old AgentConfig from agent.py with a more comprehensive
    configuration system that supports AGENT.md files.
    """

    # Basic info
    name: str
    description: str

    # LLM config
    model: str
    temperature: float = 0.7
    max_tokens: int = 16384

    # Prompts
    system_prompt: str = ""

    # Behavior
    max_turns: int = 10
    max_tool_calls_per_turn: int = 20

    # Permissions (dict format, will be converted to PermissionRuleset)
    permissions: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    source_file: Optional[Path] = None
    is_builtin: bool = False

    # Runtime config (set later)
    api_key: str = ""
    base_url: Optional[str] = None


class AgentRegistry:
    """Agent Registry - Manages all agent configurations.

    Loads agents from multiple locations with priority:
    1. Built-in: {agenix}/agents/
    2. User global: ~/.config/agenix/agents/
    3. Project local: {project}/.agenix/agents/

    Later sources override earlier ones (project > global > built-in).
    """

    _agents: Dict[str, AgentConfig] = {}
    _initialized: bool = False

    @classmethod
    def initialize(
        cls,
        working_dir: Optional[Path] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """Initialize agent registry.

        Args:
            working_dir: Working directory (for .agenix/agents/)
            api_key: API key to inject into all agents
            base_url: Base URL for API
        """
        if cls._initialized:
            return

        # Load agents from all sources
        cls._load_all_agents(working_dir)

        # Inject runtime config
        if api_key:
            for agent in cls._agents.values():
                agent.api_key = api_key
                if base_url:
                    agent.base_url = base_url

        cls._initialized = True

    @classmethod
    def _load_all_agents(cls, working_dir: Optional[Path] = None):
        """Load agents from all directories."""
        # 1. Built-in agents
        builtin_dir = Path(__file__).parent.parent / "agents"
        if builtin_dir.exists():
            cls._load_from_directory(builtin_dir, is_builtin=True)

        # 2. User global agents
        global_dir = Path.home() / ".config" / "agenix" / "agents"
        if global_dir.exists():
            cls._load_from_directory(global_dir, is_builtin=False)

        # 3. Project local agents
        if working_dir:
            local_dir = working_dir / ".agenix" / "agents"
            if local_dir.exists():
                cls._load_from_directory(local_dir, is_builtin=False)

    @classmethod
    def _load_from_directory(cls, directory: Path, is_builtin: bool):
        """Load all agents from a directory.

        Args:
            directory: Directory containing agent folders
            is_builtin: Whether these are built-in agents
        """
        for agent_dir in directory.iterdir():
            if not agent_dir.is_dir():
                continue

            agent_file = agent_dir / "AGENT.md"
            if agent_file.exists():
                try:
                    config = cls._load_agent_file(agent_file, is_builtin)
                    cls._agents[config.name] = config
                except Exception as e:
                    print(f"Warning: Failed to load agent from {agent_file}: {e}")

    @classmethod
    def _load_agent_file(cls, file: Path, is_builtin: bool) -> AgentConfig:
        """Load agent configuration from AGENT.md file.

        Args:
            file: Path to AGENT.md
            is_builtin: Whether this is a built-in agent

        Returns:
            AgentConfig object

        Raises:
            ValueError: If file format is invalid
        """
        import yaml  # Lazy import to avoid dependency at module level

        content = file.read_text()

        # Parse YAML frontmatter
        if not content.startswith("---"):
            raise ValueError(f"Invalid AGENT.md format (missing frontmatter): {file}")

        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid AGENT.md format (incomplete frontmatter): {file}")

        # Parse metadata
        metadata = yaml.safe_load(parts[1])
        if not metadata:
            raise ValueError(f"Invalid AGENT.md format (empty frontmatter): {file}")

        # Parse markdown content
        markdown = parts[2].strip()

        # Extract system prompt from markdown
        system_prompt = cls._extract_system_prompt(markdown)

        # Build AgentConfig
        return AgentConfig(
            name=metadata["name"],
            description=metadata.get("description", ""),
            model=metadata.get("model", "gpt-4"),
            temperature=metadata.get("temperature", 0.7),
            max_tokens=metadata.get("max_tokens", 16384),
            max_turns=metadata.get("max_turns", 10),
            max_tool_calls_per_turn=metadata.get("max_tool_calls_per_turn", 20),
            system_prompt=system_prompt,
            permissions=metadata.get("permissions", {}),
            source_file=file,
            is_builtin=is_builtin,
        )

    @classmethod
    def _extract_system_prompt(cls, markdown: str) -> str:
        """Extract system prompt from markdown content.

        Looks for ## System Prompt section and extracts content until next ## heading.

        Args:
            markdown: Markdown content (without frontmatter)

        Returns:
            Extracted system prompt text
        """
        lines = markdown.split("\n")
        in_prompt = False
        prompt_lines = []

        for line in lines:
            # Start collecting at ## System Prompt
            if line.strip().startswith("## System Prompt"):
                in_prompt = True
                continue

            if in_prompt:
                # Stop at next ## heading
                if line.strip().startswith("##"):
                    break
                prompt_lines.append(line)

        return "\n".join(prompt_lines).strip()

    @classmethod
    def get(cls, name: str) -> Optional[AgentConfig]:
        """Get agent configuration by name.

        Args:
            name: Agent name

        Returns:
            AgentConfig or None if not found
        """
        if not cls._initialized:
            cls.initialize()

        return cls._agents.get(name)

    @classmethod
    def list(cls, include_builtin: bool = True) -> List[AgentConfig]:
        """List all registered agents.

        Args:
            include_builtin: Whether to include built-in agents

        Returns:
            List of AgentConfig objects
        """
        if not cls._initialized:
            cls.initialize()

        agents = list(cls._agents.values())

        if not include_builtin:
            agents = [a for a in agents if not a.is_builtin]

        return agents

    @classmethod
    def list_names(cls, include_builtin: bool = True) -> List[str]:
        """List names of all registered agents.

        Args:
            include_builtin: Whether to include built-in agents

        Returns:
            List of agent names
        """
        return [a.name for a in cls.list(include_builtin=include_builtin)]

    @classmethod
    def reset(cls):
        """Reset the registry (mainly for testing)."""
        cls._agents.clear()
        cls._initialized = False

    @classmethod
    def exists(cls, name: str) -> bool:
        """Check if an agent exists.

        Args:
            name: Agent name

        Returns:
            True if agent exists, False otherwise
        """
        if not cls._initialized:
            cls.initialize()

        return name in cls._agents
