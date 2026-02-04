"""Extension runner - executes extensions and manages their lifecycle."""

import traceback
from typing import Any, Dict, List, Optional

from .types import (CommandDefinition, Event, EventType, ExtensionContext,
                    LoadedExtension, ToolDefinition)


class ExtensionRunner:
    """Manages execution of loaded extensions."""

    def __init__(
        self,
        extensions: List[LoadedExtension],
        context: ExtensionContext
    ):
        self.extensions = extensions
        self.context = context

    def get_tools(self) -> Dict[str, ToolDefinition]:
        """Get all registered custom tools from extensions."""
        tools = {}
        for ext in self.extensions:
            tools.update(ext.tools)
        return tools

    def get_commands(self) -> Dict[str, CommandDefinition]:
        """Get all registered commands from extensions."""
        commands = {}
        for ext in self.extensions:
            commands.update(ext.commands)
        return commands

    async def emit(self, event: Event) -> None:
        """Emit an event to all registered handlers.

        Args:
            event: The event to emit.
        """
        event_type = event.type

        for ext in self.extensions:
            handlers = ext.handlers.get(event_type, [])

            for handler in handlers:
                try:
                    await handler(event, self.context)
                except Exception as e:
                    print(
                        f"Error in extension {ext.name} handling {event_type}: {e}")
                    traceback.print_exc()

    async def execute_command(self, command_name: str, args: str) -> bool:
        """Execute a registered extension command.

        Args:
            command_name: Name of the command
            args: Command arguments as string

        Returns:
            True if command was found and executed, False otherwise.
        """
        for ext in self.extensions:
            command = ext.commands.get(command_name)
            if command:
                try:
                    await command.handler(self.context, args)
                    return True
                except Exception as e:
                    print(f"Error executing command {command_name}: {e}")
                    traceback.print_exc()
                    return True  # Command was found, but failed

        return False  # Command not found

    def has_handlers(self, event_type: EventType) -> bool:
        """Check if any extension has handlers for an event type."""
        for ext in self.extensions:
            if event_type in ext.handlers and len(ext.handlers[event_type]) > 0:
                return True
        return False

    def get_extension_paths(self) -> List[str]:
        """Get list of loaded extension paths."""
        return [ext.path for ext in self.extensions]

    def get_extension_names(self) -> List[str]:
        """Get list of loaded extension names."""
        return [ext.name for ext in self.extensions]
