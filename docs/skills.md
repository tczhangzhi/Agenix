# Skills Guide

Skills provide specialized instructions to the agent via progressive disclosure. Instead of loading all knowledge upfront, skills are referenced in the system prompt and loaded on-demand when needed.

## Table of Contents

- [Overview](#overview)
- [How Skills Work](#how-skills-work)
- [Built-in Skills](#built-in-skills)
- [Creating Custom Skills](#creating-custom-skills)

## Overview

Skills follow the [Anthropic Agent Skills](https://docs.anthropic.com/en/docs/build-with-claude/agent-skills) standard. They are markdown files with YAML frontmatter that provide specialized instructions for specific tasks.

**Philosophy**: Keep the system prompt minimal. Load domain knowledge only when the task requires it.

## How Skills Work

1. **Discovery**: At startup, agenix scans skill directories and adds a list of available skills to the system prompt

2. **On-Demand Loading**: When the agent recognizes a task matches a skill, it uses the `read` tool to load the skill file

3. **Progressive Disclosure**: Only the skills needed for the current task are loaded, keeping context minimal

## Built-in Skills

Agenix ships with 7 default skills:

### pdf
Process and extract content from PDF files.

**Use when**: Working with PDF documents, extracting text, analyzing PDF structure

### xlsx
Handle Excel spreadsheet operations.

**Use when**: Reading, writing, or analyzing Excel files

### docx
Process Microsoft Word documents.

**Use when**: Working with .docx files, extracting content, modifying documents

### pptx
Handle PowerPoint presentations.

**Use when**: Reading or creating presentation files

### browser-use
Automate browser interactions using Chrome DevTools Protocol (CDP).

**Use when**: Web scraping, browser automation, testing web applications

### find-skills
Discover and search available skills.

**Use when**: User asks "what can you do" or needs help finding appropriate skills

### skill-creator
Guide for creating new custom skills.

**Use when**: User wants to create their own skills

## Creating Custom Skills

### Quick Start

1. Create a directory: `~/.agenix/skills/my-skill/`
2. Add `SKILL.md` file with frontmatter
3. Write instructions in markdown

### Minimal Example

```markdown
---
name: my-skill
description: Brief description of what this skill does
---

# My Skill

Use this skill when the user asks about X.

## Steps

1. First, do this
2. Then, do that
3. Finally, verify the result

## Examples

Example of expected usage...
```

### Full Example with All Fields

```markdown
---
name: database-helper
description: PostgreSQL database operations and queries
license: MIT
compatibility: Python 3.8+
allowed-tools:
  - Bash(psql:*)
  - Read
  - Write
metadata:
  author: Your Name
  version: 1.0.0
  tags:
    - database
    - postgresql
    - sql
---

# Database Helper

Use this skill when the user needs to:
- Connect to PostgreSQL databases
- Run SQL queries
- Analyze database schema
- Optimize queries

## Prerequisites

Ensure PostgreSQL client is installed:
```bash
psql --version
```

...
```

## Debugging Skills

### Check Loaded Skills

In interactive mode:

```
> /help
Available skills: pdf, xlsx, docx, pptx, browser-use, find-skills, skill-creator
```

### Test Skill Loading

```python
from agenix.core.skills import SkillManager

manager = SkillManager(skill_dirs=["~/.agenix/skills"])
skills = manager.list_skills()

for skill in skills:
    print(f"{skill.name}: {skill.description}")
```

### Verify Skill Format

```python
manager = SkillManager(skill_dirs=["~/.agenix/skills"])
skill = manager.get_skill("my-skill")

if skill:
    print(f"✅ Loaded: {skill.name}")
    print(f"Description: {skill.description}")
else:
    print("❌ Failed to load skill")
```

## Sharing Skills

### As Files

Share the skill directory:

```bash
# Package skill
tar -czf my-skill.tar.gz ~/.agenix/skills/my-skill/

# Install skill
tar -xzf my-skill.tar.gz -C ~/.agenix/skills/
```

### Via Git

```bash
# Clone skills repository
git clone https://github.com/user/agenix-skills ~/.agenix/skills/
```

### Include in Projects

Add to project `.agenix/skills/` directory for project-specific skills.

## Next Steps

- [CLI Reference](cli.md) - Command-line usage
- [SDK Documentation](sdk.md) - Programmatic usage
- [Extensions Guide](../EXTENSIONS.md) - Build custom tools
- [Settings Reference](settings.md) - Configuration options
