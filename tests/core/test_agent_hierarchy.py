"""Tests for Agent hierarchy features - agent_id and parent_chain."""

import pytest

from agenix.core.agent import Agent, AgentConfig


class TestAgentHierarchy:
    """Test Agent hierarchy tracking features."""

    def test_agent_has_unique_id(self, mock_provider):
        """Test that each agent has a unique ID."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="test-key", provider=mock_provider)
        agent1 = Agent(config=config, tools=[])
        agent2 = Agent(config=config, tools=[])

        assert agent1.agent_id is not None
        assert agent2.agent_id is not None
        assert agent1.agent_id != agent2.agent_id

    def test_agent_custom_id(self, mock_provider):
        """Test creating agent with custom ID."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="test-key", provider=mock_provider)
        custom_id = "my-custom-agent-id"
        agent = Agent(config=config, tools=[], agent_id=custom_id)

        assert agent.agent_id == custom_id

    def test_agent_parent_chain_default_empty(self, mock_provider):
        """Test that parent_chain defaults to empty list."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="test-key", provider=mock_provider)
        agent = Agent(config=config, tools=[])

        assert agent.parent_chain == []

    def test_agent_with_parent_chain(self, mock_provider):
        """Test creating agent with parent chain."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="test-key", provider=mock_provider)
        parent_chain = ["parent-agent-1", "parent-agent-2"]
        agent = Agent(config=config, tools=[], parent_chain=parent_chain)

        assert agent.parent_chain == parent_chain
        assert len(agent.parent_chain) == 2

    def test_parent_chain_immutability(self, mock_provider):
        """Test that parent_chain is properly tracked."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="test-key", provider=mock_provider)

        # Create root agent
        root_agent = Agent(config=config, tools=[], agent_id="root")
        assert root_agent.parent_chain == []

        # Create child agent with root in parent chain
        child_agent = Agent(
            config=config,
            tools=[],
            agent_id="child",
            parent_chain=[root_agent.agent_id]
        )
        assert len(child_agent.parent_chain) == 1
        assert "root" in child_agent.parent_chain

    def test_multi_level_parent_chain(self, mock_provider):
        """Test multi-level parent chain (grandparent -> parent -> child)."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="test-key", provider=mock_provider)

        # Level 1: Grandparent
        grandparent = Agent(config=config, tools=[], agent_id="grandparent")

        # Level 2: Parent
        parent = Agent(
            config=config,
            tools=[],
            agent_id="parent",
            parent_chain=[grandparent.agent_id]
        )

        # Level 3: Child
        child = Agent(
            config=config,
            tools=[],
            agent_id="child",
            parent_chain=parent.parent_chain + [parent.agent_id]
        )

        assert child.parent_chain == ["grandparent", "parent"]
        assert len(child.parent_chain) == 2

    def test_agent_id_in_parent_chain_detection(self, mock_provider):
        """Test detecting if an agent ID is in the parent chain."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="test-key", provider=mock_provider)

        agent = Agent(
            config=config,
            tools=[],
            agent_id="child",
            parent_chain=["ancestor-1", "ancestor-2", "parent"]
        )

        # Check if specific IDs are in parent chain
        assert "ancestor-1" in agent.parent_chain
        assert "ancestor-2" in agent.parent_chain
        assert "parent" in agent.parent_chain
        assert "non-existent" not in agent.parent_chain

    def test_agent_id_type(self, mock_provider):
        """Test that agent_id is a string."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="test-key", provider=mock_provider)
        agent = Agent(config=config, tools=[])

        assert isinstance(agent.agent_id, str)
        assert len(agent.agent_id) > 0


class TestAgentHierarchyUseCases:
    """Test real-world use cases for agent hierarchy."""

    def test_circular_reference_prevention_data_structure(self, mock_provider):
        """Test data structure supports circular reference prevention."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="test-key", provider=mock_provider)

        # Create agent A
        agent_a = Agent(config=config, tools=[], agent_id="agent-a")

        # Create agent B as child of A
        agent_b = Agent(
            config=config,
            tools=[],
            agent_id="agent-b",
            parent_chain=[agent_a.agent_id]
        )

        # If B tries to spawn A again, we can detect it
        would_be_circular = agent_a.agent_id in agent_b.parent_chain
        assert would_be_circular is True  # B knows A is its parent

    def test_delegation_chain_tracking(self, mock_provider):
        """Test tracking delegation chains for debugging."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="test-key", provider=mock_provider)

        # Main agent delegates to explorer
        main_agent = Agent(config=config, tools=[], agent_id="main")

        explorer_agent = Agent(
            config=config,
            tools=[],
            agent_id="explorer",
            parent_chain=[main_agent.agent_id]
        )

        # Explorer delegates to file reader
        file_reader_agent = Agent(
            config=config,
            tools=[],
            agent_id="file-reader",
            parent_chain=explorer_agent.parent_chain + [explorer_agent.agent_id]
        )

        # File reader can trace back to main
        delegation_chain = file_reader_agent.parent_chain + [file_reader_agent.agent_id]
        assert delegation_chain == ["main", "explorer", "file-reader"]

    def test_agent_without_hierarchy_params_still_works(self, mock_provider):
        """Test backward compatibility - agents work without hierarchy params."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="test-key", provider=mock_provider)

        # Create agent without specifying agent_id or parent_chain
        agent = Agent(config=config, tools=[])

        # Should still work with defaults
        assert agent.agent_id is not None
        assert agent.parent_chain is not None
        assert agent.messages == []
        assert agent.tool_map == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
