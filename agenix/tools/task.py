"""Task Tool - Delegate tasks to specialized subagents.

This tool implements the "Agent as Tool" design pattern, allowing the main agent
to create and delegate to specialized subagents with different permissions and capabilities.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List

from .base import Tool, ToolResult


class TaskTool(Tool):
    """Task Tool - Create subagents to execute specialized tasks.

    This tool allows delegating tasks to specialized agents with different:
    - Permissions (e.g., read-only for exploration)
    - Models (e.g., faster models for simple tasks)
    - Prompts (e.g., specialized instructions)

    Subagents are loaded from AGENT.md files in the same search paths as skills.

    Example:
        >>> task_tool = TaskTool(parent_agent="build")
        >>> result = await task_tool.execute(
        ...     tool_call_id="123",
        ...     arguments={
        ...         "agent": "explore",
        ...         "task": "Find all API endpoints"
        ...     }
        ... )
    """

    def __init__(
        self,
        working_dir: str = ".",
        agent_id: Optional[str] = None,
        parent_chain: Optional[List[str]] = None
    ):
        """Initialize Task Tool.

        Args:
            working_dir: Working directory (for agent registry)
            agent_id: Unique ID of the current agent (for preventing circular calls)
            parent_chain: List of ancestor agent IDs (for preventing circular calls)
        """
        self.working_dir = working_dir
        self.agent_id = agent_id
        self.parent_chain = parent_chain or []

        # Get available agents from registry
        # Note: This will be updated once we implement the new agent registry
        self._available_agents = self._get_available_agents()

        # Build agent list description
        agent_list = self._format_agents_description()

        super().__init__(
            name="task",
            description=f"""Delegate a task to a specialized subagent.

Use this tool when:
- The task requires different permissions (e.g., read-only exploration)
- The task is complex and benefits from focused execution
- The task needs specialized expertise

{agent_list}

The subagent will execute independently and return results.""",
            parameters={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Name of the subagent to use",
                        "enum": list(self._available_agents.keys()) if self._available_agents else ["no-agents"]
                    },
                    "task": {
                        "type": "string",
                        "description": "Clear description of the task for the subagent"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional additional context or information needed for the task"
                    }
                },
                "required": ["agent", "task"]
            }
        )

    def _get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get available agents from registry.

        Returns:
            Dict mapping agent name to metadata
        """
        from ..extensions.agent_registry import AgentRegistry

        # Initialize registry if needed
        AgentRegistry.initialize(working_dir=Path(self.working_dir) if self.working_dir else None)

        # Get all agents (no filtering - we'll check for circular calls at runtime)
        agents = {}
        for agent_config in AgentRegistry.list():
            agents[agent_config.name] = {
                "description": agent_config.description,
                "model": agent_config.model,
            }

        return agents

    def _format_agents_description(self) -> str:
        """Format available agents description.

        Returns:
            Formatted string describing available agents
        """
        if not self._available_agents:
            return "No subagents available."

        lines = ["Available subagents:"]
        for name, info in sorted(self._available_agents.items()):
            desc = info.get("description", "No description")
            lines.append(f"  - **{name}**: {desc}")

        return "\n".join(lines)

    async def execute(
        self,
        tool_call_id: str,
        arguments: Dict[str, Any],
        on_update: Optional[Callable[[str], None]] = None,
    ) -> ToolResult:
        """Execute the task tool - create and run subagent.

        Args:
            tool_call_id: Unique ID for this tool call
            arguments: {"agent": "name", "task": "...", "context": "..."}
            on_update: Optional progress callback

        Returns:
            ToolResult with subagent's output
        """
        agent_name = arguments.get("agent", "")
        task = arguments.get("task", "")
        context = arguments.get("context", "")

        # Validate arguments
        if not agent_name:
            return ToolResult(
                content="Error: agent parameter is required",
                is_error=True
            )

        if not task:
            return ToolResult(
                content="Error: task parameter is required",
                is_error=True
            )

        # Check if agent exists
        if agent_name not in self._available_agents:
            available = ", ".join(sorted(self._available_agents.keys()))
            return ToolResult(
                content=f"Error: Agent '{agent_name}' not found.\n\nAvailable agents: {available}",
                is_error=True
            )

        # Report start
        if on_update:
            on_update(f"Starting subagent '{agent_name}'...")

        try:
            # TODO: Implement actual subagent execution
            # For now, return a placeholder
            result = await self._execute_subagent(
                agent_name=agent_name,
                task=task,
                context=context,
                on_update=on_update
            )

            return result

        except Exception as e:
            return ToolResult(
                content=f"Error executing subagent '{agent_name}': {str(e)}",
                is_error=True
            )

    async def _execute_subagent(
        self,
        agent_name: str,
        task: str,
        context: str,
        on_update: Optional[Callable[[str], None]] = None
    ) -> ToolResult:
        """Execute a subagent.

        Creates a real subagent instance and executes the task.

        Args:
            agent_name: Name of the agent to run
            task: Task description
            context: Additional context
            on_update: Progress callback

        Returns:
            ToolResult with subagent output
        """
        from ..extensions.agent_registry import AgentRegistry
        from ..core.agent import Agent, AgentConfig as OldAgentConfig
        from ..extensions.permission import PermissionRuleset, PermissionManager
        from .read import ReadTool
        from .write import WriteTool
        from .bash import BashTool
        from .grep import GrepTool
        from .glob import GlobTool
        from .skill import SkillTool

        # Get agent configuration
        agent_config = AgentRegistry.get(agent_name)
        if not agent_config:
            return ToolResult(
                content=f"Error: Agent '{agent_name}' not found in registry",
                is_error=True
            )

        if on_update:
            on_update(f"Initializing subagent '{agent_name}'...")

        try:
            # Check for circular calls
            # If this agent or any of its ancestors is in the parent chain, we have a cycle
            if self.agent_id and self.agent_id in self.parent_chain:
                return ToolResult(
                    content=f"Error: Circular agent call detected. Agent '{agent_name}' is already in the call chain.",
                    is_error=True
                )

            # Create permission manager
            permission_ruleset = PermissionRuleset.from_dict(agent_config.permissions)
            permission_manager = PermissionManager(permission_ruleset)

            # Create tools for subagent
            # Include TaskTool so subagent can create its own subagents
            tools = [
                ReadTool(working_dir=self.working_dir),
                WriteTool(working_dir=self.working_dir),
                BashTool(working_dir=self.working_dir),
                GrepTool(working_dir=self.working_dir),
                GlobTool(working_dir=self.working_dir),
                SkillTool(working_dir=self.working_dir),
            ]

            # Check if TaskTool is allowed by permissions
            if PermissionManager.is_tool_allowed("task", permission_ruleset):
                # Add TaskTool with updated parent chain
                # Note: We'll set the agent_id after creating the subagent
                tools.append(
                    TaskTool(
                        working_dir=self.working_dir,
                        agent_id=None,  # Will be updated after subagent creation
                        parent_chain=self.parent_chain + ([self.agent_id] if self.agent_id else [])
                    )
                )

            # Filter tools based on permissions
            allowed_tools = [
                t for t in tools
                if PermissionManager.is_tool_allowed(t.name, permission_ruleset)
            ]

            if on_update:
                on_update(f"Subagent has {len(allowed_tools)} tools available")

            # Create old-style AgentConfig (for compatibility with current Agent class)
            old_config = OldAgentConfig(
                model=agent_config.model,
                api_key=agent_config.api_key,
                base_url=agent_config.base_url,
                system_prompt=agent_config.system_prompt,
                max_turns=agent_config.max_turns,
                max_tool_calls_per_turn=agent_config.max_tool_calls_per_turn,
                max_tokens=agent_config.max_tokens,
            )

            # Create subagent with parent chain
            subagent = Agent(
                config=old_config,
                tools=allowed_tools,
                parent_chain=self.parent_chain + ([self.agent_id] if self.agent_id else [])
            )

            # Update TaskTool in subagent with the new agent_id
            for tool in allowed_tools:
                if isinstance(tool, TaskTool):
                    tool.agent_id = subagent.agent_id

            # Build full prompt
            full_prompt = task
            if context:
                full_prompt = f"Context: {context}\n\nTask: {task}"

            if on_update:
                on_update(f"Executing task...")

            # Collect subagent output
            output_parts = []
            tool_calls = []

            # Execute subagent
            async for event in subagent.prompt(full_prompt):
                # Collect text output
                from ..core.messages import MessageUpdateEvent, ToolExecutionEndEvent, AgentEndEvent

                if isinstance(event, MessageUpdateEvent):
                    output_parts.append(event.delta)
                    if on_update and event.delta:
                        on_update(event.delta)

                # Track tool calls
                elif isinstance(event, ToolExecutionEndEvent):
                    tool_calls.append({
                        "tool": event.tool_name,
                        "error": event.is_error
                    })

                # Done
                elif isinstance(event, AgentEndEvent):
                    break

            # Build result
            result_text = "".join(output_parts)

            # Add summary
            summary = f"""

---
**Subagent Execution Summary**
- Agent: {agent_name} ({agent_config.model})
- Tools available: {len(allowed_tools)}
- Tools called: {len(tool_calls)}
- Output length: {len(result_text)} characters
"""

            if tool_calls:
                summary += "\n**Tool Calls:**\n"
                for i, call in enumerate(tool_calls, 1):
                    status = "❌ Error" if call["error"] else "✓"
                    summary += f"  {i}. {call['tool']} {status}\n"

            return ToolResult(
                content=result_text + summary,
                details={
                    "agent": agent_name,
                    "model": agent_config.model,
                    "tools_available": len(allowed_tools),
                    "tools_called": len(tool_calls),
                    "output_length": len(result_text),
                }
            )

        except Exception as e:
            return ToolResult(
                content=f"Error executing subagent '{agent_name}': {str(e)}",
                is_error=True
            )
