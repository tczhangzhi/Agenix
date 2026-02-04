"""Permission Manager - Fine-grained permission control for tools.

This module implements a rule-based permission system inspired by OpenCode's
permission system, with support for:
- Allow/deny/ask actions
- Wildcard pattern matching
- Rule priority (later rules override earlier ones)
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Literal
import fnmatch


Action = Literal["allow", "deny", "ask"]


@dataclass
class Rule:
    """Permission rule.

    Examples:
        Rule("bash", "*", "allow")        # Allow all bash commands
        Rule("bash", "rm -rf *", "deny")  # Deny dangerous commands
        Rule("read", "*.env", "ask")      # Ask before reading .env files
    """

    permission: str  # Tool name or wildcard (e.g., "bash", "read", "*")
    pattern: str     # Argument pattern or wildcard (e.g., "*.py", "/tmp/*")
    action: Action   # "allow" | "deny" | "ask"

    def matches(self, tool_name: str, pattern: str = "*") -> bool:
        """Check if this rule matches the given tool and pattern.

        Args:
            tool_name: Name of the tool
            pattern: Pattern to match (e.g., file path, command)

        Returns:
            True if rule matches, False otherwise
        """
        return (
            self._match_wildcard(tool_name, self.permission) and
            self._match_wildcard(pattern, self.pattern)
        )

    @staticmethod
    def _match_wildcard(text: str, pattern: str) -> bool:
        """Match text against wildcard pattern.

        Args:
            text: Text to match
            pattern: Wildcard pattern (supports * and ?)

        Returns:
            True if matches, False otherwise
        """
        return fnmatch.fnmatch(text, pattern)


@dataclass
class PermissionRuleset:
    """Permission ruleset - collection of rules.

    Rules are evaluated from last to first (later rules have higher priority).
    """

    rules: List[Rule]

    def __init__(self, rules: List[Rule] = None):
        """Initialize ruleset.

        Args:
            rules: List of rules (optional)
        """
        self.rules = rules or []

    def evaluate(self, tool_name: str, pattern: str = "*") -> Action:
        """Evaluate permission for a tool and pattern.

        Args:
            tool_name: Name of the tool
            pattern: Pattern to match (e.g., file path)

        Returns:
            Action to take ("allow", "deny", or "ask")
        """
        # Evaluate from last to first (later rules override earlier)
        for rule in reversed(self.rules):
            if rule.matches(tool_name, pattern):
                return rule.action

        # Default: ask user
        return "ask"

    def add(self, permission: str, pattern: str, action: Action):
        """Add a rule to the ruleset.

        Args:
            permission: Tool name or wildcard
            pattern: Pattern to match
            action: Action to take
        """
        self.rules.append(Rule(permission, pattern, action))

    def merge(self, other: "PermissionRuleset") -> "PermissionRuleset":
        """Merge with another ruleset.

        Args:
            other: Ruleset to merge with

        Returns:
            New ruleset with combined rules
        """
        return PermissionRuleset(self.rules + other.rules)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "PermissionRuleset":
        """Create ruleset from configuration dictionary.

        Supports two config formats:

        Format 1 (action-based):
        {
            "allow": ["read", "glob"],
            "deny": ["bash"],
            "ask": ["write"]
        }

        Format 2 (tool-based):
        {
            "*": "allow",              # Default allow all
            "bash": {
                "*": "allow",
                "rm -rf *": "deny"     # Deny dangerous commands
            },
            "read": {
                "*.env": "ask"         # Ask before reading .env
            }
        }

        Args:
            config: Configuration dictionary

        Returns:
            PermissionRuleset object
        """
        ruleset = cls()

        # Check if using action-based format (has "allow"/"deny"/"ask" keys)
        if "allow" in config or "deny" in config or "ask" in config:
            # Format 1: {"allow": ["read", "glob"], "deny": ["bash"]}
            for action in ["allow", "deny", "ask"]:
                if action in config:
                    tools = config[action]
                    if isinstance(tools, list):
                        for tool in tools:
                            ruleset.add(tool, "*", action)
                    elif isinstance(tools, str):
                        ruleset.add(tools, "*", action)
        else:
            # Format 2: {"bash": "allow", "read": {"*.env": "ask"}}
            for key, value in config.items():
                if isinstance(value, str):
                    # Simple rule: "bash": "allow"
                    ruleset.add(key, "*", value)
                elif isinstance(value, dict):
                    # Nested rules: "bash": {"*": "allow", "rm": "deny"}
                    for pattern, action in value.items():
                        ruleset.add(key, pattern, action)

        return ruleset

    def to_dict(self) -> Dict[str, Any]:
        """Convert ruleset to dictionary format.

        Returns:
            Dictionary with "rules" key containing list of rule dicts
        """
        return {
            "rules": [
                {
                    "permission": rule.permission,
                    "pattern": rule.pattern,
                    "action": rule.action
                }
                for rule in self.rules
            ]
        }


class PermissionManager:
    """Permission Manager - Manages tool permissions for an agent.

    This is a simplified version for Phase 2. Full implementation with
    interactive permission requests will come in Phase 3.
    """

    def __init__(self, ruleset: PermissionRuleset):
        """Initialize permission manager.

        Args:
            ruleset: Permission ruleset to use
        """
        self.ruleset = ruleset

    def check(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Check if tool execution is allowed.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            True if allowed

        Raises:
            PermissionDeniedError: If permission is denied

        Note:
            In this simplified version, "ask" is treated as "allow".
            Full implementation with interactive prompts will come in Phase 3.
        """
        # Extract pattern from arguments
        pattern = self._extract_pattern(tool_name, arguments)

        # Evaluate permission
        action = self.ruleset.evaluate(tool_name, pattern)

        # Deny: raise error
        if action == "deny":
            raise PermissionDeniedError(
                f"Permission denied for tool '{tool_name}' with pattern '{pattern}'",
                tool=tool_name,
                reason=f"Denied by permission rule"
            )

        # Allow or ask: return True
        # For now, treat "ask" as "allow" (simplified)
        # Full implementation will prompt user in Phase 3
        return True

    def _extract_pattern(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Extract pattern from tool arguments.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            Pattern string for permission matching
        """
        # File operations
        if tool_name in ("read", "write", "edit"):
            return arguments.get("file_path", arguments.get("path", "*"))

        # Bash commands
        if tool_name == "bash":
            command = arguments.get("command", "")
            # Extract first word (command name)
            return command.split()[0] if command else "*"

        # Search tools
        if tool_name in ("grep", "glob"):
            return arguments.get("pattern", "*")

        # Default
        return "*"

    @staticmethod
    def is_tool_allowed(tool_name: str, ruleset: PermissionRuleset) -> bool:
        """Check if a tool is allowed at all (for tool filtering).

        Args:
            tool_name: Name of the tool
            ruleset: Permission ruleset

        Returns:
            True if tool is not permanently denied, False otherwise
        """
        action = ruleset.evaluate(tool_name, "*")
        return action != "deny"


# Exceptions
class PermissionDeniedError(Exception):
    """Raised when permission is denied."""

    def __init__(self, message: str, tool: str = "", reason: str = ""):
        """Initialize permission denied error.

        Args:
            message: Error message
            tool: Tool name that was denied
            reason: Reason for denial
        """
        super().__init__(message)
        self.tool = tool
        self.reason = reason

