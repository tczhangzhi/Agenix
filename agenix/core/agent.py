"""Agent runtime with tool execution loop."""

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Dict, List, Optional

from ..tools.base import Tool
from .llm import LLMProvider, StreamEvent
from .messages import (AgentEndEvent, AgentStartEvent, AssistantMessage, Event,
                       Message, MessageEndEvent, MessageStartEvent,
                       MessageUpdateEvent, TextContent, ToolCall,
                       ToolExecutionEndEvent, ToolExecutionStartEvent,
                       ToolExecutionUpdateEvent, ToolResultMessage,
                       TurnEndEvent, TurnStartEvent, UserMessage)


@dataclass
class AgentConfig:
    """Agent configuration."""
    model: str
    api_key: str
    base_url: Optional[str] = None
    system_prompt: Optional[str] = None
    max_turns: int = 10  # Maximum conversation turns per prompt
    max_tool_calls_per_turn: int = 20  # Maximum tool calls per turn
    max_tokens: int = 16384  # Maximum tokens for LLM output (default: 16384 for modern models)
    skill_dirs: Optional[List[str]] = None  # Directories to load skills from

    def __post_init__(self):
        """Create provider after initialization."""
        # Auto-detect provider from base_url or use OpenAI-compatible by default
        try:
            from .llm import OpenAIProvider
            self.provider = OpenAIProvider(
                api_key=self.api_key, base_url=self.base_url)
        except Exception as e:
            raise ValueError(f"Failed to initialize LLM provider: {e}")


class Agent:
    """Agent runtime with tool execution loop."""

    def __init__(self, config: AgentConfig, tools: Optional[List[Tool]] = None):
        self.config = config
        self.tools = tools or []
        self.messages: List[Message] = []
        self.subscribers: List[Callable[[Event], None]] = []

        # Build tool lookup
        self.tool_map = {tool.name: tool for tool in self.tools}

        # Initialize skill manager
        from .skills import SkillManager
        self.skill_manager = SkillManager(skill_dirs=config.skill_dirs)

        # Inject skills into system prompt
        self._inject_skills_into_system_prompt()

    def _inject_skills_into_system_prompt(self):
        """Inject available skills into system prompt.

        Uses simple, clear format following pi-mono's approach.
        Skills provide specialized instructions via progressive disclosure.
        """
        skills = self.skill_manager.list_skills()
        visible_skills = [s for s in skills if not s.disable_model_invocation]

        if not visible_skills:
            return

        # Simple, clear instructions (pi-mono style)
        instructions = []
        instructions.append("\n\n")
        instructions.append(
            "The following skills provide specialized instructions for specific tasks.\n")
        instructions.append(
            "Use the read tool to load a skill's file when the task matches its description.\n")
        instructions.append(
            "When a skill file references a relative path, resolve it against the skill directory.\n")
        instructions.append("\n")
        instructions.append("<available_skills>\n")

        # Add skills with name, description, and location (XML format)
        for skill in visible_skills:
            instructions.append("  <skill>\n")
            instructions.append(
                f"    <name>{self._escape_xml(skill.name)}</name>\n")
            instructions.append(
                f"    <description>{self._escape_xml(skill.description)}</description>\n")
            instructions.append(
                f"    <location>{self._escape_xml(skill.file_path)}</location>\n")
            instructions.append("  </skill>\n")

        instructions.append("</available_skills>\n")

        # Append to system prompt
        if self.config.system_prompt:
            self.config.system_prompt += "".join(instructions)

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters."""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

    def subscribe(self, callback: Callable[[Event], None]) -> Callable[[], None]:
        """Subscribe to agent events.

        Returns:
            Unsubscribe function
        """
        self.subscribers.append(callback)
        return lambda: self.subscribers.remove(callback)

    def _emit(self, event: Event) -> None:
        """Emit event to all subscribers."""
        for callback in self.subscribers:
            try:
                callback(event)
            except Exception as e:
                # Don't let subscriber errors break the agent
                print(f"Error in event subscriber: {e}")

    async def prompt(self, user_message: str) -> AsyncIterator[Event]:
        """Process a user prompt through the agent loop.

        Args:
            user_message: User's message

        Yields:
            Agent events
        """
        # Add user message
        msg = UserMessage(content=user_message)
        self.messages.append(msg)

        # Run agent loop
        async for event in self._run_loop():
            yield event

    async def _run_loop(self) -> AsyncIterator[Event]:
        """Main agent loop with tool calling."""
        # Emit agent start
        event = AgentStartEvent()
        self._emit(event)
        yield event

        for turn in range(self.config.max_turns):
            # Emit turn start
            turn_event = TurnStartEvent()
            self._emit(turn_event)
            yield turn_event

            # Get LLM response
            assistant_message = None
            async for msg_event in self._stream_llm_response():
                yield msg_event
                if isinstance(msg_event, MessageEndEvent):
                    assistant_message = msg_event.message

            if not assistant_message:
                break

            # Add to messages
            self.messages.append(assistant_message)

            # Execute tools if any
            tool_results = []
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls[:self.config.max_tool_calls_per_turn]:
                    # Validate tool call has proper arguments before execution
                    if not tool_call.arguments or not isinstance(tool_call.arguments, dict):
                        # Invalid tool call - create detailed error message
                        error_msg = ToolResultMessage(
                            tool_call_id=tool_call.id,
                            name=tool_call.name,
                            content=f"Error: Tool '{tool_call.name}' called with invalid arguments. "
                                    f"Received: {tool_call.arguments}. "
                                    f"Please check the tool's required parameters and try again with valid arguments.",
                            is_error=True
                        )
                        tool_results.append(error_msg)
                        self.messages.append(error_msg)
                        continue

                    # Execute valid tool call
                    async for tool_event in self._execute_tool(tool_call):
                        yield tool_event
                        if isinstance(tool_event, ToolExecutionEndEvent):
                            # Create tool result message
                            # Preserve structured content from ToolResult
                            from ..tools.base import ToolResult

                            result_content = tool_event.result
                            if isinstance(result_content, ToolResult):
                                # ToolResult object - extract the content field
                                result_content = result_content.content

                            result_msg = ToolResultMessage(
                                tool_call_id=tool_event.tool_call_id,
                                name=tool_event.tool_name,
                                content=result_content,  # Keep structure: str or List[TextContent|ImageContent]
                                is_error=tool_event.is_error
                            )
                            tool_results.append(result_msg)
                            self.messages.append(result_msg)

            # Emit turn end
            turn_end = TurnEndEvent(
                message=assistant_message, tool_results=tool_results)
            self._emit(turn_end)
            yield turn_end

            # Check if we should continue
            # Continue if: (1) there are tool calls, OR (2) output was truncated (length)
            should_continue = (
                bool(assistant_message.tool_calls) or
                assistant_message.stop_reason == "length"
            )

            if not should_continue:
                break

        # Emit agent end
        end_event = AgentEndEvent(messages=self.messages)
        self._emit(end_event)
        yield end_event

    async def _stream_llm_response(self) -> AsyncIterator[Event]:
        """Stream LLM response."""
        # Prepare context
        tools_dict = [tool.to_dict()
                      for tool in self.tools] if self.tools else None

        try:
            # Start streaming
            message = AssistantMessage(content=[], model=self.config.model)

            start_event = MessageStartEvent(message=message)
            self._emit(start_event)
            yield start_event

            # Collect streaming content
            text_parts = []
            tool_calls_list = []
            finish_reason = None  # Capture actual finish reason from LLM

            # Stream from LLM
            stream = self.config.provider.stream(
                model=self.config.model,
                messages=self.messages,
                system_prompt=self.config.system_prompt,
                tools=tools_dict,
                max_tokens=self.config.max_tokens,
            )

            async for event in stream:
                if event.type == "text_delta":
                    text_parts.append(event.delta)
                    # Update message
                    message.content = [TextContent(text="".join(text_parts))]

                    # Emit update
                    update_event = MessageUpdateEvent(
                        message=message, delta=event.delta)
                    self._emit(update_event)
                    yield update_event

                elif event.type == "tool_call" and event.tool_call:
                    # Complete tool call received
                    tool_calls_list.append(event.tool_call)

                elif event.type == "finish" and event.finish_reason:
                    # Capture finish reason from LLM
                    finish_reason = event.finish_reason

            # Finalize message
            if text_parts:
                message.content = [TextContent(text="".join(text_parts))]
            message.tool_calls = tool_calls_list

            # Note: We don't fetch usage info to avoid extra API call and delay
            # The streaming response should be sufficient for user interaction
            message.usage = None
            # Use actual finish_reason from LLM, fallback to inferring from content
            if finish_reason:
                message.stop_reason = finish_reason
            else:
                message.stop_reason = "stop" if not tool_calls_list else "tool_calls"

            # Emit end
            end_event = MessageEndEvent(message=message)
            self._emit(end_event)
            yield end_event

        except Exception as e:
            # Emit error
            error_msg = AssistantMessage(
                content=[TextContent(text=f"Error: {str(e)}")],
                model=self.config.model,
                stop_reason="error"
            )
            end_event = MessageEndEvent(message=error_msg)
            self._emit(end_event)
            yield end_event

    async def _execute_tool(self, tool_call: ToolCall) -> AsyncIterator[Event]:
        """Execute a tool call."""
        tool = self.tool_map.get(tool_call.name)

        # Emit start
        start_event = ToolExecutionStartEvent(
            tool_call_id=tool_call.id,
            tool_name=tool_call.name,
            args=tool_call.arguments
        )
        self._emit(start_event)
        yield start_event

        if not tool:
            # Tool not found
            end_event = ToolExecutionEndEvent(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                result=f"Error: Tool '{tool_call.name}' not found",
                is_error=True
            )
            self._emit(end_event)
            yield end_event
            return

        # Execute tool
        try:
            def on_update(partial_result: str):
                """Progress callback."""
                update_event = ToolExecutionUpdateEvent(
                    tool_call_id=tool_call.id,
                    tool_name=tool_call.name,
                    partial_result=partial_result
                )
                self._emit(update_event)
                # Note: Not yielding update events to simplify async flow

            result = await tool.execute(
                tool_call_id=tool_call.id,
                arguments=tool_call.arguments,
                on_update=on_update
            )

            # Emit end
            end_event = ToolExecutionEndEvent(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                result=result.content,
                is_error=result.is_error
            )
            self._emit(end_event)
            yield end_event

        except Exception as e:
            # Tool execution error
            end_event = ToolExecutionEndEvent(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                result=f"Error executing tool: {str(e)}",
                is_error=True
            )
            self._emit(end_event)
            yield end_event

    def get_messages(self) -> List[Message]:
        """Get conversation messages."""
        return self.messages.copy()

    def clear_messages(self) -> None:
        """Clear conversation history."""
        self.messages.clear()
