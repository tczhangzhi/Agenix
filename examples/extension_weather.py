#!/usr/bin/env python
"""Example: Custom tool extension.

This example shows how to create a custom tool extension.

Place this file in ~/.agenix/extensions/ or .agenix/extensions/
"""

import requests

from agenix.extensions import ToolDefinition


async def setup(agenix):
    """Extension setup function."""

    async def weather_execute(params, ctx):
        """Fetch weather information.

        Args:
            params: Tool parameters from LLM
            ctx: Extension context

        Returns:
            Weather information as string
        """
        city = params.get("city", "Unknown")

        # This is a mock implementation
        # In a real extension, you'd call an actual weather API
        return f"Weather in {city}: Sunny, 72°F (22°C)"

    # Register the weather tool
    agenix.register_tool(ToolDefinition(
        name="get_weather",
        description="Get current weather information for a city",
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name"
                }
            },
            "required": ["city"]
        },
        execute=weather_execute
    ))

    # Show notification
    agenix.notify("Weather tool registered!", "info")
