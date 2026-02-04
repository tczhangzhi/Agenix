"""Tests for Permission system - Access control and rules."""

import pytest

from agenix.extensions.permission import (
    PermissionDeniedError,
    PermissionManager,
    PermissionRuleset,
    Rule,
)


class TestRule:
    """Test Rule dataclass."""

    def test_create_rule(self):
        """Test creating a rule."""
        rule = Rule(permission="read", pattern="*", action="allow")

        assert rule.permission == "read"
        assert rule.pattern == "*"
        assert rule.action == "allow"

    def test_rule_matches_exact(self):
        """Test rule matching with exact match."""
        rule = Rule(permission="read", pattern="*.py", action="allow")

        assert rule.matches("read", "test.py")
        assert not rule.matches("write", "test.py")
        assert not rule.matches("read", "test.txt")

    def test_rule_matches_wildcard(self):
        """Test rule matching with wildcards."""
        rule = Rule(permission="*", pattern="*", action="allow")

        assert rule.matches("read", "anything")
        assert rule.matches("write", "anything")


class TestPermissionRuleset:
    """Test PermissionRuleset class."""

    def test_create_empty_ruleset(self):
        """Test creating empty ruleset."""
        ruleset = PermissionRuleset()

        assert ruleset.rules == []

    def test_create_ruleset_with_rules(self):
        """Test creating ruleset with rules."""
        rules = [
            Rule(permission="read", pattern="*", action="allow"),
            Rule(permission="write", pattern="*", action="deny")
        ]
        ruleset = PermissionRuleset(rules=rules)

        assert len(ruleset.rules) == 2

    def test_evaluate_with_allow_rule(self):
        """Test evaluating with allow rule."""
        ruleset = PermissionRuleset(rules=[
            Rule(permission="read", pattern="*", action="allow")
        ])

        action = ruleset.evaluate("read", "*")

        assert action == "allow"

    def test_evaluate_with_deny_rule(self):
        """Test evaluating with deny rule."""
        ruleset = PermissionRuleset(rules=[
            Rule(permission="bash", pattern="*", action="deny")
        ])

        action = ruleset.evaluate("bash", "rm -rf /")

        assert action == "deny"

    def test_evaluate_priority_last_wins(self):
        """Test that later rules override earlier ones."""
        ruleset = PermissionRuleset(rules=[
            Rule(permission="read", pattern="*", action="deny"),
            Rule(permission="read", pattern="*", action="allow")  # Last wins
        ])

        action = ruleset.evaluate("read", "*")

        assert action == "allow"

    def test_evaluate_no_match_returns_ask(self):
        """Test that no match returns 'ask'."""
        ruleset = PermissionRuleset()

        action = ruleset.evaluate("unknown_tool", "*")

        assert action == "ask"

    def test_add_rule(self):
        """Test adding rule to ruleset."""
        ruleset = PermissionRuleset()

        ruleset.add("read", "*", "allow")

        assert len(ruleset.rules) == 1
        assert ruleset.rules[0].permission == "read"

    def test_from_dict(self):
        """Test creating ruleset from dict."""
        config = {
            "allow": ["read", "glob"],
            "deny": ["bash"]
        }

        ruleset = PermissionRuleset.from_dict(config)

        # Should have rules for allow and deny
        assert len(ruleset.rules) > 0

    def test_to_dict(self):
        """Test converting ruleset to dict."""
        ruleset = PermissionRuleset(rules=[
            Rule(permission="read", pattern="*", action="allow"),
            Rule(permission="write", pattern="*", action="deny")
        ])

        config = ruleset.to_dict()

        assert isinstance(config, dict)
        assert "rules" in config


class TestPermissionManager:
    """Test PermissionManager class."""

    def test_create_manager(self):
        """Test creating manager."""
        ruleset = PermissionRuleset()
        manager = PermissionManager(ruleset)

        assert manager.ruleset == ruleset

    def test_check_allowed(self):
        """Test checking allowed permission."""
        ruleset = PermissionRuleset(rules=[
            Rule(permission="read", pattern="*", action="allow")
        ])
        manager = PermissionManager(ruleset)

        # Should allow read
        result = manager.check("read", {})
        assert result is True

    def test_check_denied_raises_error(self):
        """Test that denied permission raises error."""
        ruleset = PermissionRuleset(rules=[
            Rule(permission="bash", pattern="*", action="deny")
        ])
        manager = PermissionManager(ruleset)

        # Should raise error
        with pytest.raises(PermissionDeniedError):
            manager.check("bash", {"command": "rm -rf /"})

    def test_is_tool_allowed_static(self):
        """Test static method is_tool_allowed."""
        ruleset = PermissionRuleset(rules=[
            Rule(permission="read", pattern="*", action="allow"),
            Rule(permission="write", pattern="*", action="deny")
        ])

        # Test allowed tool
        assert PermissionManager.is_tool_allowed("read", ruleset) is True

        # Test denied tool
        assert PermissionManager.is_tool_allowed("write", ruleset) is False

    def test_empty_ruleset_asks(self):
        """Test that empty ruleset returns ask."""
        ruleset = PermissionRuleset()
        manager = PermissionManager(ruleset)

        # Empty ruleset should ask (or allow depending on implementation)
        # Check doesn't raise error
        try:
            manager.check("any_tool", {})
        except PermissionDeniedError:
            pytest.fail("Should not deny with empty ruleset")

    def test_permission_denied_error_structure(self):
        """Test PermissionDeniedError structure."""
        error = PermissionDeniedError("Access denied", tool="bash", reason="Security")

        assert error.tool == "bash"
        assert error.reason == "Security"
        assert "Access denied" in str(error)


class TestPermissionScenarios:
    """Test real-world permission scenarios."""

    def test_read_only_mode(self):
        """Test read-only permission mode."""
        ruleset = PermissionRuleset(rules=[
            Rule(permission="read", pattern="*", action="allow"),
            Rule(permission="glob", pattern="*", action="allow"),
            Rule(permission="grep", pattern="*", action="allow"),
            Rule(permission="write", pattern="*", action="deny"),
            Rule(permission="edit", pattern="*", action="deny"),
            Rule(permission="bash", pattern="*", action="deny")
        ])

        # Should allow read operations
        assert ruleset.evaluate("read") == "allow"
        assert ruleset.evaluate("glob") == "allow"
        assert ruleset.evaluate("grep") == "allow"

        # Should deny write operations
        assert ruleset.evaluate("write") == "deny"
        assert ruleset.evaluate("edit") == "deny"
        assert ruleset.evaluate("bash") == "deny"

    def test_selective_file_access(self):
        """Test selective file access patterns."""
        ruleset = PermissionRuleset(rules=[
            Rule(permission="read", pattern="*.py", action="allow"),
            Rule(permission="read", pattern="*.env", action="deny")
        ])

        # Should allow Python files
        assert ruleset.evaluate("read", "test.py") == "allow"

        # Should deny .env files
        assert ruleset.evaluate("read", "config.env") == "deny"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
