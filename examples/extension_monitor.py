#!/usr/bin/env python
"""Example: Event handler extension.

This example shows how to use event handlers to monitor agent activity.

Place this file in ~/.agenix/extensions/ or .agenix/extensions/
"""

from agenix.extensions import EventType


async def setup(agenix):
    """Extension setup function."""

    # Track statistics
    stats = {
        "tool_calls": 0,
        "tools_used": set()
    }

    @agenix.on(EventType.AGENT_START)
    async def on_agent_start(event, ctx):
        """Log when agent starts."""
        print(f"\n🚀 Agent started with prompt: {event.prompt[:50]}...")

    @agenix.on(EventType.TOOL_CALL)
    async def on_tool_call(event, ctx):
        """Track tool usage."""
        stats["tool_calls"] += 1
        stats["tools_used"].add(event.tool_name)
        print(f"🔧 Tool called: {event.tool_name}")

    @agenix.on(EventType.AGENT_END)
    async def on_agent_end(event, ctx):
        """Show statistics when agent ends."""
        print(f"\n✅ Agent finished!")
        print(f"   Total tool calls: {stats['tool_calls']}")
        print(f"   Tools used: {', '.join(sorted(stats['tools_used']))}")
        print(f"   Total messages: {len(ctx.messages)}")

    agenix.notify("Activity monitor extension loaded!", "info")
