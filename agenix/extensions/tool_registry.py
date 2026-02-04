"""Tool Registry - Load and manage tool configurations from TOOL.md files.

This module implements the tool loading system that supports:
- Built-in tools (agenix/tools/)
- User global tools (~/.config/agenix/tools/)
- Project local tools (.agenix/tools/)

Tools are defined using TOOL.md files with YAML frontmatter.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class ToolConfig:
    """Tool configuration loaded from TOOL.md.

    This allows dynamic tool loading similar to agents and skills.
    """

    # Basic info
    name: str
    description: str

    # Implementation
    module: str  # Python module path (e.g., "agenix.tools.read")
    class_name: str  # Class name (e.g., "ReadTool")

    # Parameters (optional)
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    source_file: Optional[Path] = None
    is_builtin: bool = False


class ToolRegistry:
    """Tool Registry - Manages all tool configurations.

    Loads tools from multiple locations with priority:
    1. Built-in: {agenix}/tools/
    2. User global: ~/.config/agenix/tools/
    3. Project local: {project}/.agenix/tools/

    Later sources override earlier ones (project > global > built-in).
    """

    _tools: Dict[str, ToolConfig] = {}
    _initialized: bool = False

    @classmethod
    def initialize(
        cls,
        working_dir: Optional[Path] = None,
    ):
        """Initialize tool registry.

        Args:
            working_dir: Working directory (for .agenix/tools/)
        """
        if cls._initialized:
            return

        # Load tools from all sources
        cls._load_all_tools(working_dir)

        cls._initialized = True

    @classmethod
    def _load_all_tools(cls, working_dir: Optional[Path] = None):
        """Load tools from all directories."""
        # 1. Built-in tools (note: most built-in tools are Python classes, not TOOL.md)
        builtin_dir = Path(__file__).parent.parent / "tools"
        if builtin_dir.exists():
            cls._load_from_directory(builtin_dir, is_builtin=True)

        # 2. User global tools
        global_dir = Path.home() / ".config" / "agenix" / "tools"
        if global_dir.exists():
            cls._load_from_directory(global_dir, is_builtin=False)

        # 3. Project local tools
        if working_dir:
            local_dir = working_dir / ".agenix" / "tools"
            if local_dir.exists():
                cls._load_from_directory(local_dir, is_builtin=False)

    @classmethod
    def _load_from_directory(cls, directory: Path, is_builtin: bool):
        """Load all tools from a directory.

        Args:
            directory: Directory containing tool folders
            is_builtin: Whether these are built-in tools
        """
        for tool_dir in directory.iterdir():
            if not tool_dir.is_dir():
                continue

            tool_file = tool_dir / "TOOL.md"
            if tool_file.exists():
                try:
                    config = cls._load_tool_file(tool_file, is_builtin)
                    cls._tools[config.name] = config
                except Exception as e:
                    print(f"Warning: Failed to load tool from {tool_file}: {e}")

    @classmethod
    def _load_tool_file(cls, file: Path, is_builtin: bool) -> ToolConfig:
        """Load tool configuration from TOOL.md file.

        Args:
            file: Path to TOOL.md
            is_builtin: Whether this is a built-in tool

        Returns:
            ToolConfig object

        Raises:
            ValueError: If file format is invalid
        """
        import yaml  # Lazy import to avoid dependency at module level

        content = file.read_text()

        # Parse YAML frontmatter
        if not content.startswith("---"):
            raise ValueError(f"Invalid TOOL.md format (missing frontmatter): {file}")

        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid TOOL.md format (incomplete frontmatter): {file}")

        # Parse metadata
        metadata = yaml.safe_load(parts[1])
        if not metadata:
            raise ValueError(f"Invalid TOOL.md format (empty frontmatter): {file}")

        # Build ToolConfig
        return ToolConfig(
            name=metadata["name"],
            description=metadata.get("description", ""),
            module=metadata["module"],
            class_name=metadata["class_name"],
            parameters=metadata.get("parameters", {}),
            source_file=file,
            is_builtin=is_builtin,
        )

    @classmethod
    def get(cls, name: str) -> Optional[ToolConfig]:
        """Get tool configuration by name.

        Args:
            name: Tool name

        Returns:
            ToolConfig or None if not found
        """
        if not cls._initialized:
            cls.initialize()

        return cls._tools.get(name)

    @classmethod
    def list(cls, include_builtin: bool = True) -> List[ToolConfig]:
        """List all registered tools.

        Args:
            include_builtin: Whether to include built-in tools

        Returns:
            List of ToolConfig objects
        """
        if not cls._initialized:
            cls.initialize()

        tools = list(cls._tools.values())

        if not include_builtin:
            tools = [t for t in tools if not t.is_builtin]

        return tools

    @classmethod
    def list_names(cls, include_builtin: bool = True) -> List[str]:
        """List names of all registered tools.

        Args:
            include_builtin: Whether to include built-in tools

        Returns:
            List of tool names
        """
        return [t.name for t in cls.list(include_builtin=include_builtin)]

    @classmethod
    def reset(cls):
        """Reset the registry (mainly for testing)."""
        cls._tools.clear()
        cls._initialized = False

    @classmethod
    def exists(cls, name: str) -> bool:
        """Check if a tool exists.

        Args:
            name: Tool name

        Returns:
            True if tool exists, False otherwise
        """
        if not cls._initialized:
            cls.initialize()

        return name in cls._tools

    @classmethod
    def create_tool(cls, name: str, **kwargs) -> Optional[Any]:
        """Create a tool instance from registry.

        Args:
            name: Tool name
            **kwargs: Additional parameters to pass to tool constructor

        Returns:
            Tool instance or None if not found
        """
        config = cls.get(name)
        if not config:
            return None

        try:
            # Dynamically import the module
            import importlib
            module = importlib.import_module(config.module)
            tool_class = getattr(module, config.class_name)

            # Merge config parameters with kwargs
            params = {**config.parameters, **kwargs}

            # Create tool instance
            return tool_class(**params)
        except Exception as e:
            print(f"Error creating tool '{name}': {e}")
            return None
