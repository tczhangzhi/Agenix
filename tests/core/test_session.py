"""Test suite for core.session module.

This module contains unit tests for the session management system.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from agenix.core.messages import (AssistantMessage, TextContent, Usage,
                                  UserMessage)
from agenix.core.session import SessionManager


class TestSessionManager:
    """Test cases for SessionManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)

    def test_create_session_manager(self):
        """Test creating a session manager."""
        self.setUp()
        try:
            manager = SessionManager(session_dir=self.temp_dir)

            assert manager is not None
            assert Path(self.temp_dir).exists()
        finally:
            self.tearDown()

    def test_create_session(self):
        """Test creating a new session."""
        self.setUp()
        try:
            manager = SessionManager(session_dir=self.temp_dir)
            session_id = manager.create_session("test_session")

            assert session_id == "test_session"
            session_file = Path(self.temp_dir) / f"{session_id}.jsonl"
            assert session_file.exists()
        finally:
            self.tearDown()

    def test_create_session_with_auto_id(self):
        """Test creating session with auto-generated ID."""
        self.setUp()
        try:
            manager = SessionManager(session_dir=self.temp_dir)
            session_id = manager.create_session()

            assert session_id is not None
            assert len(session_id) > 0
        finally:
            self.tearDown()

    def test_save_user_message(self):
        """Test saving a user message to session."""
        self.setUp()
        try:
            manager = SessionManager(session_dir=self.temp_dir)
            session_id = manager.create_session("test")

            msg = UserMessage(content="Hello")
            manager.save_message(session_id, msg)

            # Load and verify
            messages = manager.load_session(session_id)
            assert len(messages) == 1
            assert messages[0].content == "Hello"
        finally:
            self.tearDown()

    def test_save_assistant_message(self):
        """Test saving an assistant message to session."""
        self.setUp()
        try:
            manager = SessionManager(session_dir=self.temp_dir)
            session_id = manager.create_session("test")

            usage = Usage(input_tokens=100, output_tokens=50)
            msg = AssistantMessage(
                content=[TextContent(text="Response")],
                model="gpt-4o",
                usage=usage
            )
            manager.save_message(session_id, msg)

            # Load and verify
            messages = manager.load_session(session_id)
            assert len(messages) == 1
            assert messages[0].model == "gpt-4o"
            assert messages[0].usage.input_tokens == 100
        finally:
            self.tearDown()

    def test_load_empty_session(self):
        """Test loading a session with no messages."""
        self.setUp()
        try:
            manager = SessionManager(session_dir=self.temp_dir)
            session_id = manager.create_session("empty")

            messages = manager.load_session(session_id)
            assert len(messages) == 0
        finally:
            self.tearDown()

    def test_load_nonexistent_session(self):
        """Test loading a session that doesn't exist."""
        self.setUp()
        try:
            manager = SessionManager(session_dir=self.temp_dir)

            with pytest.raises(FileNotFoundError):
                manager.load_session("nonexistent")
        finally:
            self.tearDown()

    def test_list_sessions(self):
        """Test listing all sessions."""
        self.setUp()
        try:
            manager = SessionManager(session_dir=self.temp_dir)
            manager.create_session("session1")
            manager.create_session("session2")

            sessions = manager.list_sessions()

            assert len(sessions) == 2
            session_ids = [s["session_id"] for s in sessions]
            assert "session1" in session_ids
            assert "session2" in session_ids
        finally:
            self.tearDown()

    def test_delete_session(self):
        """Test deleting a session."""
        self.setUp()
        try:
            manager = SessionManager(session_dir=self.temp_dir)
            session_id = manager.create_session("delete_me")

            # Verify it exists
            session_file = Path(self.temp_dir) / f"{session_id}.jsonl"
            assert session_file.exists()

            # Delete it
            manager.delete_session(session_id)

            # Verify it's gone
            assert not session_file.exists()
        finally:
            self.tearDown()

    def test_save_and_load_multiple_messages(self):
        """Test saving and loading multiple messages."""
        self.setUp()
        try:
            manager = SessionManager(session_dir=self.temp_dir)
            session_id = manager.create_session("multi")

            # Save multiple messages
            msg1 = UserMessage(content="Hello")
            msg2 = AssistantMessage(content="Hi there", model="gpt-4o")
            msg3 = UserMessage(content="How are you?")

            manager.save_message(session_id, msg1)
            manager.save_message(session_id, msg2)
            manager.save_message(session_id, msg3)

            # Load and verify
            messages = manager.load_session(session_id)

            assert len(messages) == 3
            assert messages[0].role == "user"
            assert messages[1].role == "assistant"
            assert messages[2].role == "user"
        finally:
            self.tearDown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
