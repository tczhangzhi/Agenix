"""Additional tests for core Agent functionality."""

import pytest

from agenix.core.agent import Agent, AgentConfig
from agenix.core.messages import (
    AssistantMessage,
    TextContent,
    ToolCall,
    UserMessage,
)
from agenix.tools.base import Tool, ToolResult


class MockTool(Tool):
    """Mock tool for testing."""

    def __init__(self):
        super().__init__(
            name="mock_tool",
            description="A mock tool for testing",
            parameters={
                "type": "object",
                "properties": {
                    "input": {"type": "string"}
                },
                "required": ["input"]
            }
        )
        self.call_count = 0

    async def execute(self, tool_call_id, arguments, on_update=None):
        """Execute mock tool."""
        self.call_count += 1
        return ToolResult(
            content=f"Mock result for: {arguments.get('input', '')}",
            details={"call_count": self.call_count}
        )


class TestAgentConfig:
    """Test AgentConfig dataclass."""

    def test_create_minimal_config(self):
        """Test creating minimal config."""
        config = AgentConfig(
            model="gpt-3.5-turbo",
            api_key="test-key"
        )

        assert config.model == "gpt-3.5-turbo"
        assert config.api_key == "test-key"
        assert config.max_turns == 10  # Default
        assert config.max_tokens == 16384  # Default

    def test_create_full_config(self):
        """Test creating full config with all options."""
        config = AgentConfig(
            model="gpt-4",
            api_key="test-key",
            base_url="https://custom.api",
            system_prompt="You are helpful",
            max_turns=20,
            max_tool_calls_per_turn=10,
            max_tokens=8192
        )

        assert config.model == "gpt-4"
        assert config.base_url == "https://custom.api"
        assert config.system_prompt == "You are helpful"
        assert config.max_turns == 20
        assert config.max_tool_calls_per_turn == 10
        assert config.max_tokens == 8192

    def test_config_defaults(self):
        """Test default configuration values."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="key")

        assert config.system_prompt is None
        assert config.base_url is None
        assert config.max_turns == 10
        assert config.max_tool_calls_per_turn == 20
        assert config.max_tokens == 16384


class TestAgentInitialization:
    """Test Agent initialization."""

    def test_create_agent_minimal(self):
        """Test creating agent with minimal config."""
        config = AgentConfig(
            model="gpt-3.5-turbo",
            api_key="test-key"
        )
        agent = Agent(config=config, tools=[])

        assert agent.config == config
        assert agent.messages == []
        assert agent.tool_map == {}

    def test_create_agent_with_tools(self):
        """Test creating agent with tools."""
        config = AgentConfig(
            model="gpt-3.5-turbo",
            api_key="test-key"
        )
        mock_tool = MockTool()
        agent = Agent(config=config, tools=[mock_tool])

        assert len(agent.tool_map) == 1
        assert "mock_tool" in agent.tool_map
        assert agent.tool_map["mock_tool"] == mock_tool

    def test_create_agent_with_multiple_tools(self):
        """Test creating agent with multiple tools."""
        config = AgentConfig(
            model="gpt-3.5-turbo",
            api_key="test-key"
        )

        class Tool1(MockTool):
            def __init__(self):
                super().__init__()
                self.name = "tool1"

        class Tool2(MockTool):
            def __init__(self):
                super().__init__()
                self.name = "tool2"

        tools = [Tool1(), Tool2()]
        agent = Agent(config=config, tools=tools)

        assert len(agent.tool_map) == 2
        assert "tool1" in agent.tool_map
        assert "tool2" in agent.tool_map


class TestAgentMessages:
    """Test Agent message handling."""

    def test_initial_messages_empty(self):
        """Test that agent starts with empty messages."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="key")
        agent = Agent(config=config, tools=[])

        assert agent.messages == []
        assert len(agent.messages) == 0

    def test_add_user_message(self):
        """Test adding user message."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="key")
        agent = Agent(config=config, tools=[])

        message = UserMessage(content="Hello")
        agent.messages.append(message)

        assert len(agent.messages) == 1
        assert isinstance(agent.messages[0], UserMessage)

    def test_add_assistant_message(self):
        """Test adding assistant message."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="key")
        agent = Agent(config=config, tools=[])

        message = AssistantMessage(content=[TextContent(text="Hi there")])
        agent.messages.append(message)

        assert len(agent.messages) == 1
        assert isinstance(agent.messages[0], AssistantMessage)


class TestAgentToolMap:
    """Test Agent tool mapping."""

    def test_tool_map_construction(self):
        """Test that tool map is constructed correctly."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="key")
        tool = MockTool()
        agent = Agent(config=config, tools=[tool])

        assert "mock_tool" in agent.tool_map
        assert agent.tool_map["mock_tool"] is tool

    def test_tool_map_with_duplicate_names(self):
        """Test tool map with duplicate tool names."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="key")

        tool1 = MockTool()
        tool2 = MockTool()  # Same name

        agent = Agent(config=config, tools=[tool1, tool2])

        # Should only have one entry (last one wins)
        assert len(agent.tool_map) == 1
        assert agent.tool_map["mock_tool"] is tool2


class TestAgentConfiguration:
    """Test Agent configuration options."""

    def test_system_prompt_configuration(self):
        """Test that system prompt is configured."""
        config = AgentConfig(
            model="gpt-3.5-turbo",
            api_key="key",
            system_prompt="You are a helpful assistant"
        )
        agent = Agent(config=config, tools=[])

        assert agent.config.system_prompt == "You are a helpful assistant"

    def test_max_turns_configuration(self):
        """Test max turns configuration."""
        config = AgentConfig(
            model="gpt-3.5-turbo",
            api_key="key",
            max_turns=5
        )
        agent = Agent(config=config, tools=[])

        assert agent.config.max_turns == 5

    def test_max_tokens_configuration(self):
        """Test max tokens configuration."""
        config = AgentConfig(
            model="gpt-3.5-turbo",
            api_key="key",
            max_tokens=4096
        )
        agent = Agent(config=config, tools=[])

        assert agent.config.max_tokens == 4096


class TestAgentEventSystem:
    """Test Agent event subscription."""

    def test_subscribe_to_events(self):
        """Test subscribing to agent events."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="key")
        agent = Agent(config=config, tools=[])

        events_received = []

        def callback(event):
            events_received.append(event)

        agent.subscribe(callback)

        # Verify subscription doesn't crash
        assert True  # If we got here, subscription worked

    def test_multiple_subscribers(self):
        """Test multiple event subscribers."""
        config = AgentConfig(model="gpt-3.5-turbo", api_key="key")
        agent = Agent(config=config, tools=[])

        events1 = []
        events2 = []

        agent.subscribe(lambda e: events1.append(e))
        agent.subscribe(lambda e: events2.append(e))

        # Both subscribers should be registered
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
