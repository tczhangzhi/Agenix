"""Main entry point for agenix."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from .core.agent import Agent, AgentConfig
from .core.llm import get_provider
from .core.session import SessionManager
from .extensions.agent_registry import AgentRegistry
from .tools.bash import BashTool
from .tools.edit import EditTool
from .tools.grep import GrepTool
from .tools.read import ReadTool
from .tools.write import WriteTool
from .tools.glob import GlobTool
from .tools.skill import SkillTool
from .tools.task import TaskTool
from .ui.cli import CLI, CLIRenderer


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Agenix - Lightweight AI coding agent"
    )

    parser.add_argument(
        "--model",
        type=str,
        help="Model to use (e.g., gpt-4o, gpt-4, claude-3-5-sonnet-20241022)"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="API key (or set OPENAI_API_KEY env var)"
    )

    parser.add_argument(
        "--base-url",
        type=str,
        help="API base URL (optional, for OpenAI-compatible APIs)"
    )

    parser.add_argument(
        "--working-dir",
        type=str,
        default=".",
        help="Working directory for file operations (default: current directory)"
    )

    parser.add_argument(
        "--system-prompt",
        type=str,
        help="Custom system prompt"
    )

    parser.add_argument(
        "--session",
        type=str,
        help="Session ID to load"
    )

    parser.add_argument(
        "--max-turns",
        type=int,
        default=100,
        help="Maximum conversation turns per prompt (default: 100)"
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=16384,
        help="Maximum tokens for LLM output (default: 16384). Common values: 4096, 8192, 16384, 32768"
    )

    parser.add_argument(
        "message",
        nargs="*",
        help="Direct message to process (non-interactive mode)"
    )

    return parser.parse_args()


def get_default_model() -> str:
    """Get default model."""
    return "gpt-4o"


def get_default_system_prompt(tools: list) -> str:
    """Get default system prompt with dynamic guidelines based on available tools.

    Args:
        tools: List of available tool instances
    """
    import datetime

    # Get tool names
    tool_names = {tool.name for tool in tools}

    # Tool descriptions (keep it short - one line per tool)
    tool_descriptions = {
        "read": "Read file contents",
        "write": "Create or overwrite files",
        "edit": "Make surgical edits to files (find exact text and replace)",
        "bash": "Execute bash commands (ls, grep, find, etc.)",
        "grep": "Search file contents for patterns",
        "glob": "Find files matching glob patterns",
        "skill": "Load specialized instructions from SKILL.md files",
        "task": "Delegate tasks to specialized subagents",
    }

    # Build tools list
    tools_list = "\n".join([
        f"- {name}: {tool_descriptions.get(name, 'Tool')}"
        for name in sorted(tool_names)
        if name in tool_descriptions
    ])

    # Build guidelines dynamically based on available tools
    guidelines = []

    has_read = "read" in tool_names
    has_edit = "edit" in tool_names
    has_write = "write" in tool_names
    has_bash = "bash" in tool_names

    # Read before edit guideline
    if has_read and has_edit:
        guidelines.append("Use read to examine files before editing")

    # Edit guideline
    if has_edit:
        guidelines.append("Use edit for precise changes (old text must match exactly)")

    # Write guideline
    if has_write:
        guidelines.append("Use write only for new files or complete rewrites")

    # Output guideline
    if has_edit or has_write:
        guidelines.append("When summarizing your actions, output plain text directly - do NOT use cat or bash to display what you did")

    # Always include these
    guidelines.append("Be concise in your responses")
    guidelines.append("Show file paths clearly when working with files")

    guidelines_text = "\n".join([f"- {g}" for g in guidelines])

    # Get current date/time
    now = datetime.datetime.now()
    date_time = now.strftime("%A, %B %d, %Y at %I:%M:%S %p %Z")

    # Get working directory
    cwd = os.getcwd()

    return f"""You are an expert coding assistant operating inside Agenix, a coding agent harness. You help users by reading files, executing commands, editing code, and writing new files.

Available tools:
{tools_list}

Guidelines:
{guidelines_text}

Current date and time: {date_time}
Current working directory: {cwd}"""


def validate_config(args, renderer: CLIRenderer = None) -> tuple:
    """Validate configuration and return api_key, base_url, model.

    Args:
        args: Command-line arguments
        renderer: CLI renderer for interactive input (optional)

    Returns:
        tuple: (api_key, base_url, model)

    Raises:
        ValueError: If configuration is invalid and no renderer provided
    """
    # Get API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")

    # If no API key and renderer available, prompt for it
    if not api_key and renderer:
        api_key = renderer.prompt_config_input(
            "API Key",
            "OpenAI-compatible API key required",
            is_secret=True
        )
    elif not api_key:
        raise ValueError(
            "API key not found. Please set OPENAI_API_KEY environment variable "
            "or use --api-key parameter.\n\n"
            "Example:\n"
            "  export OPENAI_API_KEY='sk-...'\n"
            "  agenix\n\n"
            "Or:\n"
            "  agenix --api-key 'sk-...'"
        )

    # Get base URL (optional)
    base_url = args.base_url or os.getenv("OPENAI_BASE_URL")

    # If no base URL and renderer available, ask if user wants to provide one
    if not base_url and renderer:
        from prompt_toolkit import prompt
        from prompt_toolkit.validation import Validator

        try:
            response = prompt(
                "Use custom API base URL? (leave empty for default): ",
                default=""
            ).strip()
            if response:
                base_url = response
        except (EOFError, KeyboardInterrupt):
            pass  # Use default

    # Get model
    model = args.model or get_default_model()

    return api_key, base_url, model


def main():
    """Main entry point."""
    args = parse_args()

    # Setup working directory
    working_dir = os.path.abspath(args.working_dir)
    if not os.path.exists(working_dir):
        print(f"Error: Working directory does not exist: {working_dir}")
        sys.exit(1)

    # Check if we have a direct message (non-interactive)
    is_interactive = not args.message

    # Initialize CLI renderer for interactive mode
    cli = CLI() if is_interactive else None

    # Setup tools early so we can show them in banner
    # Note: TaskTool will be added after Agent creation (needs agent_id)
    tools = [
        ReadTool(working_dir=working_dir),
        WriteTool(working_dir=working_dir),
        EditTool(working_dir=working_dir),
        BashTool(working_dir=working_dir),
        GrepTool(working_dir=working_dir),
        GlobTool(working_dir=working_dir),
        SkillTool(working_dir=working_dir),
    ]

    # Initialize Agent Registry
    # This loads all available agents from:
    # 1. Built-in agents (agenix/agents/)
    # 2. User global agents (~/.config/agenix/agents/)
    # 3. Project local agents (.agenix/agents/)
    AgentRegistry.initialize(
        working_dir=Path(working_dir),
        api_key=None,  # Will be set later after config validation
        base_url=None
    )

    # In interactive mode, show banner first, then ask for config if needed
    if is_interactive and cli:
        # Try to get config without prompting
        api_key = args.api_key or os.getenv("OPENAI_API_KEY")
        base_url = args.base_url or os.getenv("OPENAI_BASE_URL")
        model = args.model or get_default_model()

        # Get skills from SkillTool for banner
        try:
            skill_tool = next(t for t in tools if t.name == "skill")
            skills = [{"name": name, "description": info.get("description", "")}
                      for name, info in skill_tool._available_skills.items()]
        except (StopIteration, AttributeError):
            skills = []

        # Show banner
        cli.renderer.render_welcome(model=model, tools=tools, skills=skills)

        # Now ask for config if needed
        if not api_key:
            api_key = cli.renderer.prompt_config_input(
                "API Key",
                "OpenAI-compatible API key required",
                is_secret=True
            )

        if not base_url:
            from prompt_toolkit import prompt
            try:
                response = prompt(
                    "Use custom API base URL? (leave empty for default): ",
                    default=""
                ).strip()
                if response:
                    base_url = response
            except (EOFError, KeyboardInterrupt):
                pass  # Use default
    else:
        # Non-interactive mode
        try:
            api_key, base_url, model = validate_config(args)
            skills = []  # Will be loaded later
        except ValueError as e:
            print(f"Configuration Error: {e}")
            sys.exit(1)

    # Setup agent
    try:
        config = AgentConfig(
            model=model,
            api_key=api_key,
            base_url=base_url,
            system_prompt=args.system_prompt or get_default_system_prompt(tools),
            max_turns=args.max_turns,
            max_tokens=args.max_tokens,
        )
        agent = Agent(config=config, tools=tools)

        # Add TaskTool after agent creation (needs agent_id)
        task_tool = TaskTool(
            working_dir=working_dir,
            agent_id=agent.agent_id,
            parent_chain=[]  # Main agent has no parents
        )
        agent.tools.append(task_tool)
        agent.tool_map[task_tool.name] = task_tool

        # Get skills list for UI (from SkillTool)
        if is_interactive:
            try:
                skill_tool = next(t for t in tools if t.name == "skill")
                skills = [{"name": name, "description": info.get("description", "")}
                          for name, info in skill_tool._available_skills.items()]
            except (StopIteration, AttributeError):
                skills = []
    except Exception as e:
        if is_interactive and cli:
            cli.renderer.render_error(f"Error initializing agent: {e}")
            sys.exit(1)
        else:
            print(f"Error initializing agent: {e}")
            sys.exit(1)

    # Setup session management
    session_manager = SessionManager()

    # Load session if specified
    if args.session:
        try:
            messages = session_manager.load_session(args.session)
            agent.messages = messages
            print(f"Loaded session: {args.session} ({len(messages)} messages)")
        except Exception as e:
            print(f"Error loading session: {e}")
            sys.exit(1)

    # Subscribe to agent events for session persistence
    current_session_id = args.session or session_manager.create_session()

    def on_message_end(event):
        """Save messages to session."""
        from agenix.core.messages import MessageEndEvent
        if isinstance(event, MessageEndEvent) and event.message:
            session_manager.save_message(current_session_id, event.message)

    agent.subscribe(on_message_end)

    # Run CLI
    if is_interactive:
        # Interactive mode (banner already shown in main())
        cli.run_interactive(agent, tools=tools, model=model, skills=skills, show_welcome=False)
    else:
        # Non-interactive mode
        message = " ".join(args.message)
        renderer = CLIRenderer()
        asyncio.run(process_single_message(agent, message, renderer))


async def process_single_message(agent, message: str, renderer: CLIRenderer):
    """Process a single message in non-interactive mode."""
    try:
        renderer.render_message("user", message)

        async for event in agent.prompt(message):
            renderer.render_event(event)

    except Exception as e:
        renderer.render_error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
