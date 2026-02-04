#!/usr/bin/env python
"""Example: Basic SDK usage.

This example shows how to use agenix as a library in your Python application.
"""

import asyncio
import os

from agenix import create_session


async def main():
    """Main function demonstrating SDK usage."""

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    print("Creating agent session...")
    session = await create_session(
        api_key=api_key,
        model="gpt-4o",
        working_dir="."
    )

    print("\n" + "="*70)
    print("Agent Session Created")
    print("="*70 + "\n")

    # Send a prompt
    print("Sending prompt: 'List Python files in current directory'")
    response = await session.prompt("List all Python files in the current directory")
    print(f"\nAgent response:\n{response}\n")

    # Continue conversation
    print("Sending prompt: 'Count total lines'")
    response = await session.prompt("How many total lines of code are there?")
    print(f"\nAgent response:\n{response}\n")

    # Check conversation history
    messages = session.get_messages()
    print(f"Conversation has {len(messages)} messages")

    # Clean up
    await session.close()
    print("\nSession closed")


if __name__ == "__main__":
    asyncio.run(main())
