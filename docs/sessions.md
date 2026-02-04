# Session Management

Understanding how Agenix manages conversation sessions.

## Table of Contents

- [Overview](#overview)
- [Session Storage](#session-storage)
- [Working with Sessions](#working-with-sessions)
- [Session Format](#session-format)
- [Session Operations](#session-operations)
- [Best Practices](#best-practices)

## Overview

Sessions in Agenix preserve conversation context across multiple interactions. Each session stores:

- Conversation messages (user, assistant, tool calls, results)
- Working directory
- Model configuration
- Timestamps
- Metadata

## Session Storage

### Default Location

```
~/.agenix/sessions/
```

### Directory Structure

Sessions are organized by working directory:

```
~/.agenix/sessions/
├── home_user_project1/
│   ├── 20240101_120000.json
│   ├── 20240101_143000.json
│   └── 20240102_090000.json
├── home_user_project2/
│   ├── 20240101_150000.json
│   └── 20240103_100000.json
└── tmp/
    └── 20240101_160000.json
```

### Session Files

Each session is a JSON file named with timestamp:

```
YYYYMMDD_HHMMSS.json
```

Example: `20240101_120000.json` = 2024-01-01 at 12:00:00

## Working with Sessions

### Auto-Save (Default)

Sessions automatically save after each interaction:

```bash
agenix
> What files are here?
# Session auto-saved to ~/.agenix/sessions/...
```

### Load Specific Session

```bash
# By full session ID
agenix --session 20240101_120000
```

### List Sessions

In interactive mode:

```bash
agenix
> /sessions
```

Output:
```
Available sessions:
  • 20240101_120000 - 2024-01-01T12:00:00Z
  • 20240101_143000 - 2024-01-01T14:30:00Z
```

### Load Session Interactively

```bash
agenix
> /load 20240101_120000
# Session loaded, conversation continues from that point
```

## Session Format

### JSON Structure

```json
{
  "id": "20240101_120000",
  "working_dir": "/home/user/project",
  "model": "gpt-4o",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:15:30Z",
  "metadata": {
    "name": "Custom Session Name",
    "tags": ["refactoring", "python"]
  },
  "messages": [
    {
      "role": "user",
      "content": "What files are in this directory?",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    {
      "role": "assistant",
      "content": [{"type": "text", "text": "I'll check..."}],
      "tool_calls": [
        {
          "id": "call_123",
          "name": "bash",
          "arguments": {"command": "ls -la"}
        }
      ],
      "timestamp": "2024-01-01T12:00:01Z"
    },
    {
      "role": "tool",
      "tool_call_id": "call_123",
      "name": "bash",
      "content": "file1.py\nfile2.py\n",
      "timestamp": "2024-01-01T12:00:02Z"
    },
    {
      "role": "assistant",
      "content": [{"type": "text", "text": "You have 2 Python files..."}],
      "timestamp": "2024-01-01T12:00:03Z"
    }
  ]
}
```

### Message Types

#### User Message

```json
{
  "role": "user",
  "content": "Your message here",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Assistant Message

```json
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "Response text"}
  ],
  "tool_calls": [
    {
      "id": "call_123",
      "name": "tool_name",
      "arguments": {"param": "value"}
    }
  ],
  "model": "gpt-4o",
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  },
  "timestamp": "2024-01-01T12:00:01Z"
}
```

#### Tool Result Message

```json
{
  "role": "tool",
  "tool_call_id": "call_123",
  "name": "tool_name",
  "content": "Tool output here",
  "is_error": false,
  "timestamp": "2024-01-01T12:00:02Z"
}
```

## Session Operations

### Creating Sessions

#### CLI

```bash
# New session (automatic)
agenix "Start new conversation"

# Specify working directory
agenix --working-dir ~/project "Start here"
```

#### SDK

```python
from agenix import create_session

# New session
session = await create_session(
    working_dir="/path/to/project"
)
```

### Loading Sessions

#### CLI

```bash
# Load specific session
agenix --session 20240101_120000
```

#### SDK

Session management in SDK is handled internally. Messages are stored in the agent instance.

### Saving Sessions

#### Automatic

Sessions auto-save after each interaction by default.

#### Manual Save

```python
from agenix.core.session import SessionManager

manager = SessionManager()
manager.save_session(session_data)
```

### Deleting Sessions

```bash
# Delete session file
rm ~/.agenix/sessions/home_user_project/20240101_120000.json

# Or delete entire directory's sessions
rm -rf ~/.agenix/sessions/home_user_project/
```

### Exporting Sessions

#### As JSON

Session files are already JSON, just copy them:

```bash
cp ~/.agenix/sessions/.../20240101_120000.json export.json
```

#### For Sharing

Remove sensitive information:

```python
import json

with open('session.json') as f:
    session = json.load(f)

# Remove working directory paths
session['working_dir'] = '/project'

# Remove tool outputs with sensitive data
for msg in session['messages']:
    if msg['role'] == 'tool' and 'api_key' in msg['content']:
        msg['content'] = '[REDACTED]'

with open('session_clean.json', 'w') as f:
    json.dump(session, f, indent=2)
```

### Importing Sessions

```bash
# Copy to sessions directory
cp exported_session.json ~/.agenix/sessions/home_user_project/

# Load in CLI
agenix --session exported_session
```

## Best Practices

### Organization

1. **Use descriptive working directories**: Helps organize sessions

```bash
agenix --working-dir ~/projects/website
agenix --working-dir ~/projects/api
```

2. **Name your sessions**: Add metadata for better tracking

```python
session_data = {
    "metadata": {
        "name": "Refactoring auth module",
        "tags": ["refactoring", "authentication"]
    }
}
```

### Performance

1. **Clean old sessions**: Delete sessions you no longer need

```bash
# Delete sessions older than 30 days
find ~/.agenix/sessions -name "*.json" -mtime +30 -delete
```

2. **Start new sessions**: Start new sessions for unrelated tasks

```bash
# Better: New session per task
agenix "New task"
```

### Security

1. **Review before sharing**: Remove sensitive data

2. **Secure storage**: Keep sessions directory private

```bash
chmod 700 ~/.agenix/sessions
```

3. **Don't commit sessions**: Add to .gitignore

```bash
# .gitignore
.agenix/sessions/
```

### Workflow

1. **Load sessions for related work**:

```bash
# Day 1: Start refactoring
agenix "Let's refactor the auth module"

# Day 2: Load the session
agenix --session <session_id>
```

2. **New session for new tasks**:

```bash
# Don't mix unrelated work in same session
agenix "Now let's work on the frontend"
```

## Session Analysis

### Token Usage

Calculate total tokens used:

```python
import json

with open('session.json') as f:
    session = json.load(f)

total_tokens = 0
for msg in session['messages']:
    if msg['role'] == 'assistant' and 'usage' in msg:
        total_tokens += msg['usage']['total_tokens']

print(f"Total tokens: {total_tokens}")
```

### Cost Estimation

```python
# Approximate costs (as of 2024)
COSTS = {
    'gpt-4o': {
        'prompt': 0.005 / 1000,    # $0.005 per 1K tokens
        'completion': 0.015 / 1000  # $0.015 per 1K tokens
    },
    'gpt-4': {
        'prompt': 0.03 / 1000,
        'completion': 0.06 / 1000
    }
}

def estimate_cost(session_file):
    with open(session_file) as f:
        session = json.load(f)

    model = session.get('model', 'gpt-4o')
    costs = COSTS.get(model, COSTS['gpt-4o'])

    total_cost = 0
    for msg in session['messages']:
        if msg['role'] == 'assistant' and 'usage' in msg:
            usage = msg['usage']
            total_cost += usage['prompt_tokens'] * costs['prompt']
            total_cost += usage['completion_tokens'] * costs['completion']

    return total_cost

cost = estimate_cost('session.json')
print(f"Estimated cost: ${cost:.4f}")
```

### Session Statistics

```python
def analyze_session(session_file):
    with open(session_file) as f:
        session = json.load(f)

    messages = session['messages']

    stats = {
        'total_messages': len(messages),
        'user_messages': sum(1 for m in messages if m['role'] == 'user'),
        'assistant_messages': sum(1 for m in messages if m['role'] == 'assistant'),
        'tool_calls': sum(len(m.get('tool_calls', [])) for m in messages if m['role'] == 'assistant'),
        'tool_results': sum(1 for m in messages if m['role'] == 'tool')
    }

    return stats

stats = analyze_session('session.json')
print(f"Messages: {stats['total_messages']}")
print(f"Tool calls: {stats['tool_calls']}")
```

## Troubleshooting

### Session Not Found

```bash
Error: Session not found: 20240101_120000
```

**Solution**: Check available sessions

```bash
ls ~/.agenix/sessions/*/
```

### Corrupted Session

```bash
Error: Failed to load session
```

**Solution**: Validate JSON

```bash
python -m json.tool session.json
```

### Session Too Large

If sessions become too large (> 100K tokens):

1. Start a new session
2. Summarize old session if needed
3. Delete old session

## Custom Session Storage

### Change Location

```bash
export AGENIX_SESSION_DIR="/custom/path/sessions"
agenix
```

### Custom Format

Implement custom session manager:

```python
from agenix.core.session import SessionManager

class CustomSessionManager(SessionManager):
    def save_session(self, session_data):
        # Custom save logic (e.g., to database)
        pass

    def load_session(self, session_id):
        # Custom load logic
        pass
```

## Next Steps

- [CLI Reference](cli.md) - Command-line usage
- [SDK Documentation](sdk.md) - Programmatic usage
- [Settings Reference](settings.md) - Configuration
- [Skills Guide](skills.md) - Skill system
