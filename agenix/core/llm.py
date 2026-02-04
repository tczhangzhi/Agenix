"""Unified LLM interface with LiteLLM for multi-provider support."""

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from .messages import (
    AssistantMessage,
    ImageContent,
    Message,
    ReasoningContent,
    TextContent,
    ToolCall,
    ToolResultMessage,
    Usage,
    UserMessage,
)


@dataclass
class StreamEvent:
    """LLM stream event."""
    type: str  # "text_delta" | "tool_call" | "finish" | "reasoning_delta"
    delta: str = ""
    tool_call: Optional[ToolCall] = None
    finish_reason: Optional[str] = None  # "stop", "length", "tool_calls", "content_filter"
    reasoning_block_id: Optional[str] = None  # For tracking reasoning blocks


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def stream(
        self,
        model: str,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
    ) -> AsyncIterator[StreamEvent]:
        """Stream LLM responses."""
        pass

    @abstractmethod
    async def complete(
        self,
        model: str,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
    ) -> AssistantMessage:
        """Complete LLM request (non-streaming)."""
        pass

    def _messages_to_dict(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert messages to API format."""
        result = []
        for msg in messages:
            if isinstance(msg, UserMessage):
                result.append({
                    "role": "user",
                    "content": msg.content if isinstance(msg.content, str) else self._format_content(msg.content)
                })
            elif isinstance(msg, AssistantMessage):
                entry = {"role": "assistant"}
                if isinstance(msg.content, str):
                    entry["content"] = msg.content
                else:
                    # Extract text content
                    text_parts = [
                        c.text for c in msg.content if isinstance(c, TextContent)]
                    if text_parts:
                        entry["content"] = "\n".join(text_parts)
                    else:
                        # No text content - set empty string to satisfy API requirements
                        entry["content"] = ""

                    # Add tool calls if present
                    if msg.tool_calls:
                        entry["tool_calls"] = [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.name,
                                    "arguments": json.dumps(tc.arguments)
                                }
                            }
                            for tc in msg.tool_calls
                        ]
                result.append(entry)
            elif isinstance(msg, ToolResultMessage):
                formatted_content = msg.content
                if isinstance(msg.content, list):
                    formatted_content = self._format_content(msg.content)
                    # If _format_content returns a list (contains images), we need to:
                    # 1. First send a tool message with text only (to satisfy OpenAI's requirement)
                    # 2. Then send a user message with images
                    if isinstance(formatted_content, list):
                        # Extract text parts for tool response
                        text_parts = [item["text"] for item in formatted_content if item["type"] == "text"]
                        tool_response = "\n".join(text_parts) if text_parts else "[Image content]"

                        # Add tool message (required by OpenAI API)
                        result.append({
                            "role": "tool",
                            "tool_call_id": msg.tool_call_id,
                            "content": tool_response
                        })

                        # Add user message with images
                        result.append({
                            "role": "user",
                            "content": formatted_content
                        })
                        continue

                result.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "content": formatted_content if isinstance(formatted_content, str) else str(formatted_content)
                })
        return result

    def _format_content(self, content: List[Any]) -> Union[str, List[Dict]]:
        """Format mixed content, preserving images."""
        # Check if content is text-only
        is_text_only = all(isinstance(item, TextContent) for item in content)

        if is_text_only:
            # Text-only: return simple string for backward compatibility
            return "\n".join([item.text for item in content])

        # Rich content: build list of content blocks
        result = []
        for item in content:
            if isinstance(item, TextContent):
                result.append({
                    "type": "text",
                    "text": item.text
                })
            elif isinstance(item, ImageContent):
                # OpenAI format: data URL with base64
                result.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{item.source['media_type']};base64,{item.source['data']}"
                    }
                })
            else:
                # Fallback for unknown content types: convert to text
                result.append({
                    "type": "text",
                    "text": str(item) if not hasattr(item, 'text') else item.text
                })

        return result


class LiteLLMProvider(LLMProvider):
    """LiteLLM provider for multi-model support.

    Supports multiple providers through LiteLLM:
    - OpenAI (openai/gpt-4, gpt-4o, o1-*, etc.)
    - Anthropic (anthropic/claude-*, claude-*)
    - Google Gemini (gemini/gemini-*, gemini-*)
    - OpenRouter (openrouter/*, auto-prefixed if sk-or-* key)
    - Groq (groq/*)
    - Custom endpoints (auto-detect provider from model name)
    - Many others supported by LiteLLM

    Environment variables:
    - AGENIX_API_KEY: API key for the provider
    - AGENIX_MODEL: Default model to use
    - AGENIX_BASE_URL: Custom API base URL (optional)
    - AGENIX_REASONING_EFFORT: Reasoning effort level (low/medium/high)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
    ):
        """Initialize LiteLLM provider.

        Args:
            api_key: API key for the provider
            base_url: Custom API base URL
            model: Default model to use
            reasoning_effort: Reasoning effort for thinking models (low/medium/high)
        """
        try:
            import litellm
            from litellm import acompletion
            self._litellm = litellm
            self._acompletion = acompletion
        except ImportError:
            raise ImportError(
                "litellm package required. Install with: pip install litellm"
            )

        super().__init__(api_key=api_key, base_url=base_url)

        self.default_model = model or os.getenv("AGENIX_MODEL", "gpt-4o")
        self.reasoning_effort = reasoning_effort or os.getenv("AGENIX_REASONING_EFFORT")

        # Detect provider from model name or API key or base_url
        self.is_openrouter = (
            (api_key and api_key.startswith("sk-or-"))
            or (base_url and "openrouter" in base_url)
            or self.default_model.startswith("openrouter/")
        )

        # Detect custom endpoint (but not openrouter)
        self.is_custom_endpoint = bool(base_url) and not self.is_openrouter

        # Configure LiteLLM
        self._configure_litellm()

        # Disable LiteLLM verbose logging
        self._litellm.suppress_debug_info = True

    def _configure_litellm(self):
        """Configure LiteLLM based on provider."""
        if not self.api_key:
            return

        # Set API key based on provider
        if self.is_openrouter:
            os.environ["OPENROUTER_API_KEY"] = self.api_key
        elif self.is_custom_endpoint:
            # For custom endpoints, detect provider from model name
            if "claude" in self.default_model.lower() or "anthropic" in self.default_model.lower():
                # Custom endpoint with Claude model (e.g., aihubmix)
                os.environ["ANTHROPIC_API_KEY"] = self.api_key
            else:
                # Default to OpenAI-compatible
                os.environ["OPENAI_API_KEY"] = self.api_key
        elif "anthropic" in self.default_model or "claude" in self.default_model:
            os.environ.setdefault("ANTHROPIC_API_KEY", self.api_key)
        elif "openai" in self.default_model or "gpt" in self.default_model or "o1" in self.default_model:
            os.environ.setdefault("OPENAI_API_KEY", self.api_key)
        elif "gemini" in self.default_model.lower() or "google" in self.default_model.lower():
            os.environ.setdefault("GEMINI_API_KEY", self.api_key)
        elif "groq" in self.default_model:
            os.environ.setdefault("GROQ_API_KEY", self.api_key)
        else:
            # Default to OpenAI-compatible
            os.environ.setdefault("OPENAI_API_KEY", self.api_key)

        # Set base URL if provided
        if self.base_url:
            self._litellm.api_base = self.base_url

    def _normalize_model_name(self, model: str) -> str:
        """Normalize model name for LiteLLM.

        Args:
            model: Raw model name

        Returns:
            Normalized model name with proper prefix
        """
        # OpenRouter
        if self.is_openrouter and not model.startswith("openrouter/"):
            return f"openrouter/{model}"

        # Custom endpoint - detect provider from model name
        if self.is_custom_endpoint:
            # Don't add prefix if already has one
            if "/" in model:
                return model

            # Detect provider from model name
            if "claude" in model.lower():
                return f"anthropic/{model}"
            elif "gemini" in model.lower():
                return f"gemini/{model}"
            else:
                # Default to openai/ for other custom endpoints
                return f"openai/{model}"

        # Gemini
        if "gemini" in model.lower() and not model.startswith("gemini/"):
            return f"gemini/{model}"

        # Anthropic/Claude
        if "claude" in model and not (
            model.startswith("anthropic/") or model.startswith("claude-")
        ):
            return f"anthropic/{model}"

        return model

    async def stream(
        self,
        model: str,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
    ) -> AsyncIterator[StreamEvent]:
        """Stream responses using LiteLLM.

        Args:
            model: Model name
            messages: List of messages
            system_prompt: System prompt
            tools: Tool definitions
            max_tokens: Maximum tokens

        Yields:
            StreamEvent instances
        """
        model = self._normalize_model_name(model)

        # Build API messages
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend(self._messages_to_dict(messages))

        # Build kwargs
        kwargs = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "stream": True,
        }

        if self.base_url:
            kwargs["api_base"] = self.base_url

        if tools:
            kwargs["tools"] = [self._convert_tool(t) for t in tools]
            kwargs["tool_choice"] = "auto"

        # Add reasoning effort for OpenAI o1 models
        if self.reasoning_effort and "o1" in model:
            kwargs["reasoning_effort"] = self.reasoning_effort

        try:
            response = await self._acompletion(**kwargs)

            # Accumulate tool calls and reasoning
            tool_calls_accumulator = {}
            reasoning_buffer = {}
            finish_reason = None

            async for chunk in response:
                if not hasattr(chunk, "choices") or not chunk.choices:
                    continue

                choice = chunk.choices[0]

                # Capture finish reason
                if hasattr(choice, "finish_reason") and choice.finish_reason:
                    finish_reason = choice.finish_reason

                delta = choice.delta if hasattr(choice, "delta") else None
                if not delta:
                    continue

                # Handle text delta
                if hasattr(delta, "content") and delta.content:
                    yield StreamEvent(type="text_delta", delta=delta.content)

                # Handle reasoning/thinking content
                reasoning_text = None
                reasoning_id = "reasoning_0"

                # Check for various thinking/reasoning attributes
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    reasoning_text = delta.reasoning_content
                elif hasattr(delta, "thinking_blocks") and delta.thinking_blocks:
                    # thinking_blocks is a list of dicts with 'thinking' field
                    if isinstance(delta.thinking_blocks, list):
                        thinking_texts = []
                        for block in delta.thinking_blocks:
                            if isinstance(block, dict) and 'thinking' in block:
                                thinking_text = block['thinking']
                                # Skip empty or signature-only blocks
                                if thinking_text and thinking_text.strip():
                                    thinking_texts.append(thinking_text)
                        if thinking_texts:
                            reasoning_text = "\n".join(thinking_texts)
                    else:
                        reasoning_text = str(delta.thinking_blocks)
                elif hasattr(delta, "reasoning") and delta.reasoning:
                    reasoning_text = delta.reasoning

                if reasoning_text:
                    if reasoning_id not in reasoning_buffer:
                        reasoning_buffer[reasoning_id] = ""

                    reasoning_buffer[reasoning_id] += reasoning_text
                    yield StreamEvent(
                        type="reasoning_delta",
                        delta=reasoning_text,
                        reasoning_block_id=reasoning_id
                    )
                    continue  # Skip text delta handling for this chunk

                # Handle tool calls
                if hasattr(delta, "tool_calls") and delta.tool_calls:
                    for tc in delta.tool_calls:
                        tc_index = tc.index if hasattr(tc, "index") and tc.index is not None else 0
                        tc_id = tc.id if hasattr(tc, "id") else f"call_{tc_index}"

                        if tc_index not in tool_calls_accumulator:
                            tool_calls_accumulator[tc_index] = {
                                "id": tc_id,
                                "name": "",
                                "arguments": ""
                            }

                        if hasattr(tc, "id") and tc.id:
                            tool_calls_accumulator[tc_index]["id"] = tc.id

                        if hasattr(tc, "function") and tc.function:
                            if hasattr(tc.function, "name") and tc.function.name:
                                tool_calls_accumulator[tc_index]["name"] = tc.function.name
                            if hasattr(tc.function, "arguments") and tc.function.arguments:
                                tool_calls_accumulator[tc_index]["arguments"] += tc.function.arguments

            # Yield complete tool calls
            for tc_data in tool_calls_accumulator.values():
                if not tc_data["arguments"] or not tc_data["arguments"].strip():
                    arguments = {}
                else:
                    try:
                        arguments = json.loads(tc_data["arguments"])
                    except json.JSONDecodeError:
                        arguments = {}

                yield StreamEvent(
                    type="tool_call",
                    tool_call=ToolCall(
                        id=tc_data["id"],
                        name=tc_data["name"],
                        arguments=arguments
                    )
                )

            # Yield finish reason
            if finish_reason:
                yield StreamEvent(type="finish", finish_reason=finish_reason)

        except Exception as e:
            # Log error for debugging
            import sys
            print(f"\n❌ LiteLLM Error: {type(e).__name__}: {str(e)}", file=sys.stderr)
            print(f"Model: {model}", file=sys.stderr)
            print(f"Base URL: {self.base_url}", file=sys.stderr)
            # Re-raise to let caller handle
            raise

    async def complete(
        self,
        model: str,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
    ) -> AssistantMessage:
        """Complete request using LiteLLM.

        Args:
            model: Model name
            messages: List of messages
            system_prompt: System prompt
            tools: Tool definitions
            max_tokens: Maximum tokens

        Returns:
            AssistantMessage with response
        """
        model = self._normalize_model_name(model)

        # Build API messages
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend(self._messages_to_dict(messages))

        # Build kwargs
        kwargs = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
        }

        if self.base_url:
            kwargs["api_base"] = self.base_url

        if tools:
            kwargs["tools"] = [self._convert_tool(t) for t in tools]
            kwargs["tool_choice"] = "auto"

        # Add reasoning effort for OpenAI o1 models
        if self.reasoning_effort and "o1" in model:
            kwargs["reasoning_effort"] = self.reasoning_effort

        try:
            response = await self._acompletion(**kwargs)

            choice = response.choices[0]
            message = choice.message

            # Build content
            content_parts = []
            tool_calls = []

            if hasattr(message, "content") and message.content:
                content_parts.append(TextContent(text=message.content))

            # Handle reasoning/thinking
            if hasattr(message, "reasoning") and message.reasoning:
                content_parts.append(ReasoningContent(
                    text=message.reasoning,
                    reasoning_id="reasoning"
                ))

            # Handle tool calls
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tc in message.tool_calls:
                    args = tc.function.arguments
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {}

                    tool_calls.append(ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=args
                    ))

            # Handle usage
            usage = None
            if hasattr(response, "usage") and response.usage:
                usage = Usage(
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                )

            return AssistantMessage(
                content=content_parts,
                tool_calls=tool_calls,
                model=model,
                usage=usage,
                stop_reason=choice.finish_reason or "stop",
            )

        except Exception as e:
            # Log error for debugging
            import sys
            print(f"\n❌ LiteLLM Error: {type(e).__name__}: {str(e)}", file=sys.stderr)
            print(f"Model: {model}", file=sys.stderr)
            print(f"Base URL: {self.base_url}", file=sys.stderr)
            raise

    def _convert_tool(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Convert tool definition to OpenAI format."""
        return {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool.get("parameters", {})
            }
        }


# Default provider
def get_provider(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    reasoning_effort: Optional[str] = None,
) -> LLMProvider:
    """Get LiteLLM provider instance.

    Args:
        api_key: API key for the provider
        base_url: Custom API base URL
        model: Default model to use
        reasoning_effort: Reasoning effort for thinking models

    Returns:
        LiteLLMProvider instance
    """
    return LiteLLMProvider(
        api_key=api_key,
        base_url=base_url,
        model=model,
        reasoning_effort=reasoning_effort,
    )
