"""CLI interface for agenix."""

import os
import sys
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..core.messages import (Event, ImageContent, MessageEndEvent,
                             MessageStartEvent, MessageUpdateEvent, TextContent,
                             ToolExecutionEndEvent, ToolExecutionStartEvent,
                             ToolExecutionUpdateEvent, TurnEndEvent,
                             TurnStartEvent)
from ..tools.base import ToolResult


class CLIRenderer:
    """Render agent events to terminal."""

    def __init__(self):
        self.console = Console()
        self.current_message = ""
        self.current_tool = None
        self.current_tool_args = None  # Store tool args
        self.message_buffer = []  # For buffering streaming content
        self.in_live_mode = False
        self.tool_output_lines = []  # Store tool output lines

        # Initialize prompt session with better unicode support
        self.prompt_session = PromptSession(
            style=Style.from_dict({
                'prompt': '#0066cc bold',  # Blue bold for prompt
            })
        )

    def render_event(self, event: Event) -> None:
        """Render an event to the console."""
        if isinstance(event, TurnStartEvent):
            pass  # Don't show separator

        elif isinstance(event, MessageStartEvent):
            self.current_message = ""
            self.message_buffer = []

        elif isinstance(event, MessageUpdateEvent):
            # Accumulate message
            self.current_message += event.delta
            self.message_buffer.append(event.delta)

        elif isinstance(event, MessageEndEvent):
            # Show assistant message in a box when complete
            if self.current_message:
                self.console.print()
                self.console.print(Panel(
                    self.current_message.strip(),
                    border_style="green",
                    box=box.ROUNDED,
                    padding=(0, 1),
                    title="[bold green]Assistant[/bold green]",
                    title_align="left"
                ))
            self.current_message = ""
            self.message_buffer = []

        elif isinstance(event, ToolExecutionStartEvent):
            self.current_tool = event.tool_name
            self.current_tool_args = event.args if hasattr(event, 'args') else None
            self.tool_output_lines = []

        elif isinstance(event, ToolExecutionUpdateEvent):
            # Collect tool output
            if event.partial_result:
                result_str = str(event.partial_result)
                lines = result_str.split('\n')
                self.tool_output_lines.extend(lines)

        elif isinstance(event, ToolExecutionEndEvent):
            # Show tool execution in a box
            if event.result:
                # Handle both ToolResult objects and direct content
                content = event.result

                # If event.result is a list (structured content with text/images)
                if isinstance(content, list):
                    # Mixed content (text + images)
                    result_parts = []
                    for item in content:
                        if isinstance(item, TextContent):
                            result_parts.append(item.text)
                        elif isinstance(item, ImageContent):
                            # Show image placeholder
                            media_type = item.source.get('media_type', 'image')
                            result_parts.append(f"[Image: {media_type}]")
                        else:
                            # Fallback: try to convert to string
                            if hasattr(item, 'text'):
                                result_parts.append(item.text)
                            else:
                                result_parts.append(str(item))
                    result_str = '\n'.join(result_parts)
                elif isinstance(content, ToolResult):
                    # ToolResult object - extract content
                    if isinstance(content.content, list):
                        result_parts = []
                        for item in content.content:
                            if isinstance(item, TextContent):
                                result_parts.append(item.text)
                            elif isinstance(item, ImageContent):
                                media_type = item.source.get('media_type', 'image')
                                result_parts.append(f"[Image: {media_type}]")
                        result_str = '\n'.join(result_parts)
                    else:
                        result_str = str(content.content)
                else:
                    result_str = str(content)

                all_lines = result_str.split('\n')

                # Get last 8 non-empty lines
                display_lines = [line for line in all_lines if line.strip()][-8:]

                if display_lines:
                    output_text = '\n'.join(display_lines)

                    # Build tool title with args
                    tool_title = f"[cyan]{self.current_tool}[/cyan]"

                    # Add key arg to title
                    if self.current_tool_args:
                        if 'file_path' in self.current_tool_args:
                            tool_title += f" [dim]{self.current_tool_args['file_path']}[/dim]"
                        elif 'pattern' in self.current_tool_args:
                            tool_title += f" [dim]{self.current_tool_args['pattern']}[/dim]"
                        elif 'command' in self.current_tool_args:
                            cmd = self.current_tool_args['command']
                            if len(cmd) > 40:
                                cmd = cmd[:37] + "..."
                            tool_title += f" [dim]{cmd}[/dim]"

                    border_color = "red" if event.is_error else "magenta"
                    title_text = f"[bold]Tool: {tool_title}[/bold]"

                    self.console.print()
                    self.console.print(Panel(
                        output_text,
                        border_style=border_color,
                        box=box.ROUNDED,
                        padding=(0, 1),
                        title=title_text,
                        title_align="left"
                    ))

            self.current_tool = None
            self.current_tool_args = None
            self.tool_output_lines = []

        elif isinstance(event, TurnEndEvent):
            # Show token usage
            if event.message and event.message.usage:
                usage = event.message.usage
                total_tokens = usage.input_tokens + usage.output_tokens
                self.console.print(
                    f"[dim]{total_tokens:,} tokens[/dim]"
                )

    def render_message(self, role: str, content: str, is_error: bool = False) -> None:
        """Render a complete message in a box."""
        if role == "user":
            self.console.print()
            self.console.print(Panel(
                content,
                border_style="blue",
                box=box.ROUNDED,
                padding=(0, 1),
                title="[bold blue]You[/bold blue]",
                title_align="left"
            ))
        elif role == "assistant":
            self.console.print()
            self.console.print(Panel(
                content,
                border_style="green",
                box=box.ROUNDED,
                padding=(0, 1),
                title="[bold green]Assistant[/bold green]",
                title_align="left"
            ))
        elif role == "system":
            style = "red" if is_error else "yellow"
            self.console.print()
            self.console.print(Panel(
                content,
                border_style=style,
                box=box.ROUNDED,
                padding=(0, 1),
                title=f"[bold {style}]System[/bold {style}]",
                title_align="left"
            ))

    def render_error(self, error: str) -> None:
        """Render an error."""
        error_text = error if error and error.strip() else "Unknown error occurred"
        self.console.print(Panel(
            f"[bold red]Error:[/bold red] {error_text}",
            border_style="red",
            padding=(1, 2)
        ))

    def render_welcome(self, model: str = None, tools=None, skills=None) -> None:
        """Render welcome banner with ASCII art."""
        from .. import __version__

        # ASCII art for Agenix
        ascii_art = Text.from_markup("""[cyan]   _                    _
  / \\   __ _  ___ _ __ (_)_  __
 / _ \\ / _` |/ _ \\ '_ \\| \\ \\/ /
/ ___ \\ (_| |  __/ | | | |>  <
/_/   \\_\\__, |\\___|_| |_|_/_/\\_\\
        |___/[/cyan]""")

        # Get working directory (shortened if too long)
        cwd = os.getcwd()
        home = os.path.expanduser("~")
        if cwd.startswith(home):
            cwd = "~" + cwd[len(home):]

        # Build right side info
        info_text = Text()
        info_text.append(f"Version {__version__}", style="dim")
        info_text.append("\n\n")
        info_text.append("Model: ", style="cyan")
        info_text.append(model or 'gpt-4o')
        info_text.append("\n")
        info_text.append("Working Directory: ", style="cyan")
        info_text.append(cwd)
        info_text.append("\n\n")
        info_text.append("Commands: ", style="yellow")
        info_text.append("/help /clear /sessions /quit")

        # Skills (if any)
        if skills and len(skills) > 0:
            info_text.append("\n")
            info_text.append("Skills: ", style="green")
            skill_names = [s.name for s in skills[:10]]
            skills_str = ", ".join(skill_names)
            if len(skills) > 10:
                skills_str += f" ... ({len(skills) - 10} more)"
            info_text.append(skills_str)

        # Create two-column layout
        layout = Table.grid(expand=True, padding=(0, 3))
        layout.add_column(justify="left", no_wrap=True)
        layout.add_column(justify="left")

        layout.add_row(ascii_art, info_text)

        # Create panel
        panel = Panel(
            layout,
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        )

        self.console.print(panel)

    def prompt_config_input(self, field_name: str, description: str, is_secret: bool = False) -> str:
        """Prompt user for configuration input.

        Args:
            field_name: Name of the configuration field
            description: Description of what this field is for
            is_secret: If True, input will be hidden

        Returns:
            The user input
        """
        from prompt_toolkit import prompt as pt_prompt
        from prompt_toolkit.validation import Validator, ValidationError

        class NonEmptyValidator(Validator):
            def validate(self, document):
                if not document.text.strip():
                    raise ValidationError(
                        message='This field is required',
                        cursor_position=len(document.text)
                    )

        self.console.print(
            f"[bold yellow]{description}[/bold yellow]"
        )

        try:
            value = pt_prompt(
                f"{field_name}: ",
                validator=NonEmptyValidator(),
                is_password=is_secret
            )
            return value.strip()
        except (EOFError, KeyboardInterrupt):
            self.console.print("[red]Configuration cancelled[/red]")
            sys.exit(0)

    def prompt(self, text: str = ">") -> str:
        """Show input prompt with better unicode support."""
        try:
            # Use prompt_toolkit for better unicode handling (especially Chinese)
            return self.prompt_session.prompt(f"{text} ")
        except EOFError:
            return "/quit"
        except KeyboardInterrupt:
            return "/quit"

    def clear(self) -> None:
        """Clear the screen."""
        self.console.clear()


class CLI:
    """Main CLI interface."""

    def __init__(self, renderer: Optional[CLIRenderer] = None):
        self.renderer = renderer or CLIRenderer()
        self.tools = None  # Store tools for /help command
        self.model = None  # Store model name
        self.skills = None  # Store skills list

    def run_interactive(self, agent, tools=None, model=None, skills=None, show_welcome=True) -> None:
        """Run interactive chat loop."""
        import asyncio

        self.tools = tools  # Store for /help command
        self.model = model  # Store model name
        self.skills = skills  # Store skills

        # Show welcome only if requested (main() may have already shown it)
        if show_welcome:
            self.renderer.render_welcome(model=model, tools=tools, skills=skills)

        while True:
            try:
                # Get user input
                user_input = self.renderer.prompt()

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    if not self.handle_command(user_input, agent):
                        break
                    continue

                # Process message
                asyncio.run(self.process_message(agent, user_input))

            except KeyboardInterrupt:
                self.renderer.render_message("system", "\nUse /quit to exit")
                continue
            except Exception as e:
                self.renderer.render_error(str(e))

    async def process_message(self, agent, user_input: str) -> None:
        """Process a user message."""
        try:
            # Stream agent response
            async for event in agent.prompt(user_input):
                self.renderer.render_event(event)

        except KeyboardInterrupt:
            self.renderer.render_message("system", "\nInterrupted by user")
        except Exception as e:
            import traceback
            # Show error to user - this is an LLM/API error, not a tool error
            error_msg = f"{type(e).__name__}: {str(e)}"
            if "--debug" in sys.argv:
                error_msg += f"\n\nTraceback:\n{traceback.format_exc()}"
            self.renderer.render_error(error_msg)

    def handle_command(self, command: str, agent) -> bool:
        """Handle CLI commands.

        Returns:
            True to continue, False to exit
        """
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd in ["/quit", "/exit"]:
            self.renderer.render_message("system", "Goodbye!")
            return False

        elif cmd == "/help":
            self.renderer.render_welcome(model=self.model, tools=self.tools, skills=self.skills)

        elif cmd == "/clear":
            agent.clear_messages()
            self.renderer.clear()
            self.renderer.render_message("system", "Conversation cleared")

        elif cmd == "/sessions":
            self.list_sessions()

        elif cmd == "/load":
            if args:
                self.load_session(agent, args)
            else:
                self.renderer.render_message(
                    "system", "Usage: /load <session_id>", is_error=True)

        else:
            self.renderer.render_message(
                "system", f"Unknown command: {cmd}", is_error=True)

        return True

    def list_sessions(self) -> None:
        """List saved sessions."""
        from ..core.session import SessionManager

        manager = SessionManager()
        sessions = manager.list_sessions()

        if not sessions:
            self.renderer.render_message("system", "No saved sessions")
            return

        self.renderer.console.print("\n[bold]Saved Sessions:[/bold]")
        for session in sessions:
            self.renderer.console.print(
                f"  • {session['session_id']} - {session['created_at']}"
            )

    def load_session(self, agent, session_id: str) -> None:
        """Load a session."""
        from ..core.session import SessionManager

        try:
            manager = SessionManager()
            messages = manager.load_session(session_id)

            agent.messages = messages
            self.renderer.render_message(
                "system",
                f"Loaded session: {session_id} ({len(messages)} messages)"
            )
        except FileNotFoundError:
            self.renderer.render_error(f"Session not found: {session_id}")
        except Exception as e:
            self.renderer.render_error(f"Error loading session: {str(e)}")
