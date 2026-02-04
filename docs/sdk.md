# SDK Documentation

Use Agenix as a Python library in your applications.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Advanced Usage](#advanced-usage)
- [Integration Patterns](#integration-patterns)

## Installation

```bash
pip install agenix
```

## Quick Start

```python
import asyncio
from agenix import create_session

async def main():
    # Create a session
    session = await create_session(
        api_key="your-openai-api-key",
        model="gpt-4o",
        working_dir="."
    )

    # Send a prompt
    response = await session.prompt("List all Python files in the current directory")
    print(response)

    # Continue conversation
    response = await session.prompt("Can you read main.py?")
    print(response)

    # Clean up
    await session.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### create_session()

Create a new agent session.

```python
async def create_session(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: str = "gpt-4o",
    system_prompt: Optional[str] = None,
    working_dir: str = ".",
    max_turns: int = 10,
    enable_extensions: bool = True
) -> AgentSession
```

**Parameters:**

- `api_key` (str, optional) - API key for authentication. If not provided, reads from environment:
  - `OPENAI_API_KEY` for OpenAI models
  - `ANTHROPIC_API_KEY` for Claude models

- `base_url` (str, optional) - Custom API endpoint for OpenAI-compatible providers

- `model` (str) - Model identifier. Default: `"gpt-4o"`
  - OpenAI: `gpt-4o`, `gpt-4`, etc.
  - Anthropic: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`

- `system_prompt` (str, optional) - Custom system prompt to override defaults

- `working_dir` (str) - Working directory for file operations. Default: current directory

- `max_turns` (int) - Maximum conversation turns per prompt. Default: 10

- `enable_extensions` (bool) - Whether to load extensions. Default: True

**Returns:** `AgentSession` instance

**Example:**

```python
session = await create_session(
    api_key="sk-...",
    model="gpt-4o",
    working_dir="/path/to/project",
    max_turns=20
)
```

### AgentSession

Main session class for interacting with the agent.

#### prompt()

Send a message to the agent and get response.

```python
async def prompt(self, message: str) -> str
```

**Parameters:**
- `message` (str) - User message to send

**Returns:** Complete assistant response as string

**Example:**

```python
response = await session.prompt("What files are here?")
print(response)
```

#### get_messages()

Get conversation history.

```python
def get_messages(self) -> List[Message]
```

**Returns:** List of all messages in the conversation

**Example:**

```python
messages = session.get_messages()
print(f"Total messages: {len(messages)}")

for msg in messages:
    print(f"{msg.role}: {msg.content}")
```

#### clear_messages()

Clear conversation history.

```python
def clear_messages() -> None
```

**Example:**

```python
session.clear_messages()
```

#### close()

Clean up resources and close the session.

```python
async def close() -> None
```

**Example:**

```python
await session.close()
```

## Examples

### Basic Conversation

```python
import asyncio
from agenix import create_session

async def basic_example():
    session = await create_session(model="gpt-4o")

    response = await session.prompt("Hello! What can you help me with?")
    print(f"Agent: {response}")

    response = await session.prompt("List files in current directory")
    print(f"Agent: {response}")

    await session.close()

asyncio.run(basic_example())
```

### Code Analysis

```python
import asyncio
from agenix import create_session

async def analyze_code():
    session = await create_session(
        model="gpt-4",
        working_dir="/path/to/project"
    )

    # Analyze structure
    structure = await session.prompt("Summarize the codebase structure")
    print(structure)

    # Review specific file
    review = await session.prompt("Review src/main.py for potential bugs")
    print(review)

    # Get suggestions
    suggestions = await session.prompt("Suggest improvements")
    print(suggestions)

    await session.close()

asyncio.run(analyze_code())
```

### Automated Code Generation

```python
import asyncio
from agenix import create_session

async def generate_tests():
    session = await create_session(
        model="gpt-4o",
        system_prompt="You are a Python testing expert"
    )

    # Generate tests
    await session.prompt(
        "Read src/calculator.py and generate comprehensive pytest tests"
    )

    # Verify tests exist
    result = await session.prompt("Run the tests with pytest")

    if "passed" in result.lower():
        print("✅ Tests generated and passing!")
    else:
        print("❌ Tests need fixes")

    await session.close()

asyncio.run(generate_tests())
```

### Interactive CLI Tool

```python
import asyncio
from agenix import create_session

async def interactive_cli():
    session = await create_session()

    print("Agenix Chat (type 'quit' to exit)")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ['quit', 'exit']:
            break

        if not user_input:
            continue

        response = await session.prompt(user_input)
        print(f"\nAgent: {response}")

    await session.close()
    print("Goodbye!")

asyncio.run(interactive_cli())
```

### Web API Integration

```python
from fastapi import FastAPI
from agenix import create_session

app = FastAPI()

# Create session at startup
@app.on_event("startup")
async def startup():
    app.state.session = await create_session(model="gpt-4o")

@app.on_event("shutdown")
async def shutdown():
    await app.state.session.close()

@app.post("/ask")
async def ask(question: str):
    response = await app.state.session.prompt(question)
    return {"response": response}

@app.post("/analyze")
async def analyze(file_path: str):
    prompt = f"Analyze {file_path} and provide insights"
    response = await app.state.session.prompt(prompt)
    return {"analysis": response}
```

### Batch Processing

```python
import asyncio
from pathlib import Path
from agenix import create_session

async def batch_process():
    session = await create_session(model="gpt-4o")

    # Get all Python files
    files = list(Path(".").glob("**/*.py"))

    results = []
    for file in files:
        print(f"Processing {file}...")

        response = await session.prompt(
            f"Add type hints and docstrings to {file}"
        )

        results.append({
            "file": str(file),
            "status": "completed" if "error" not in response.lower() else "failed"
        })

    await session.close()

    # Summary
    success = sum(1 for r in results if r["status"] == "completed")
    print(f"\n✅ Processed {success}/{len(results)} files successfully")

asyncio.run(batch_process())
```

### Context Management

```python
import asyncio
from agenix import create_session

async def with_context():
    # Automatic cleanup with async context manager
    session = await create_session()

    try:
        response = await session.prompt("Your task here")
        print(response)
    finally:
        await session.close()

# Or use asyncio.run which handles cleanup
asyncio.run(with_context())
```

## Advanced Usage

### Custom System Prompt

```python
session = await create_session(
    system_prompt="""
You are an expert Python developer specializing in:
- Clean, maintainable code
- Comprehensive testing
- Security best practices
- Performance optimization

Always provide code examples and explain your reasoning.
"""
)
```

### Extension Integration

```python
# Extensions are loaded automatically from:
# - ~/.agenix/extensions/
# - .agenix/extensions/

# Create a custom extension
# .agenix/extensions/logger.py
async def setup(agenix):
    from agenix.extensions import EventType

    @agenix.on(EventType.AGENT_START)
    async def on_start(event, ctx):
        print("🤖 Agent started!")

    @agenix.on(EventType.TOOL_CALL)
    async def on_tool(event, ctx):
        print(f"🔧 Tool: {event.tool_name}")

# Extensions load automatically when creating session
session = await create_session(enable_extensions=True)
```

### Error Handling

```python
import asyncio
from agenix import create_session

async def robust_usage():
    session = None
    try:
        session = await create_session()
        response = await session.prompt("Your task")
        return response

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        if session:
            await session.close()

result = asyncio.run(robust_usage())
```

### Streaming Responses

For real-time response streaming, access the agent directly:

```python
from agenix import create_session

async def stream_example():
    session = await create_session()

    # Access underlying agent for streaming
    async for event in session.agent.prompt("Your message"):
        from agenix.core.messages import MessageUpdateEvent

        if isinstance(event, MessageUpdateEvent):
            print(event.delta, end="", flush=True)

    await session.close()

asyncio.run(stream_example())
```

## Integration Patterns

### Discord Bot

```python
import discord
from agenix import create_session

bot = discord.Client()
session = None

@bot.event
async def on_ready():
    global session
    session = await create_session()
    print(f"Bot ready as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!ask"):
        question = message.content[5:]
        response = await session.prompt(question)
        await message.channel.send(response)

bot.run("YOUR_TOKEN")
```

### Slack Bot

```python
from slack_bolt.async_app import AsyncApp
from agenix import create_session

app = AsyncApp(token="xoxb-...")
session = None

@app.event("app_mention")
async def handle_mention(event, say):
    global session
    if not session:
        session = await create_session()

    text = event["text"]
    response = await session.prompt(text)
    await say(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(app.start())
```

### Jupyter Notebook

```python
# In Jupyter notebook
from agenix import create_session

# Create session (in one cell)
session = await create_session()

# Use in multiple cells
response = await session.prompt("Analyze this dataset")
display(response)

# Continue in another cell
stats = await session.prompt("Calculate statistics")
display(stats)

# Clean up when done
await session.close()
```

## Best Practices

1. **Always close sessions**: Use `finally` blocks or context managers

2. **Reuse sessions**: Create one session for related tasks

3. **Set appropriate max_turns**: Lower for simple tasks, higher for complex ones

4. **Handle errors gracefully**: Wrap in try/except blocks

5. **Use working_dir**: Set to project root for file operations

6. **Choose right model**:
   - `gpt-4o` for speed and cost
   - `gpt-4` or Claude for complex reasoning

## Next Steps

- [CLI Reference](cli.md) - Command-line usage
- [Extensions Guide](../EXTENSIONS.md) - Build custom extensions
- [Skills Guide](skills.md) - Progressive disclosure system
- [API Documentation](api/index.html) - Full API reference (pdoc generated)
