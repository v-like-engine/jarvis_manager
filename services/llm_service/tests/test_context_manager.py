"""
Unit tests for ContextManager
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from context_manager import ContextManager, Message


@pytest.fixture
def context_manager():
    """Create ContextManager instance"""
    return ContextManager(max_exchanges=5, max_tokens_per_exchange=200)


def test_initialization(context_manager):
    """Test ContextManager initialization"""
    assert context_manager is not None
    assert context_manager.max_exchanges == 5
    assert context_manager.max_tokens_per_exchange == 200


def test_create_session(context_manager):
    """Test creating a new session"""
    session_id = context_manager.create_session()
    assert session_id is not None
    assert session_id in context_manager.sessions
    assert context_manager.current_session_id == session_id


def test_add_message(context_manager):
    """Test adding messages to session"""
    session_id = context_manager.create_session()

    context_manager.add_user_message("Hello", session_id)
    context_manager.add_assistant_message("Hi there", session_id)

    history = context_manager.get_history(session_id)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Hello"
    assert history[1].role == "assistant"
    assert history[1].content == "Hi there"


def test_get_history(context_manager):
    """Test getting conversation history"""
    session_id = context_manager.create_session()

    # Add some messages
    for i in range(4):
        context_manager.add_user_message(f"User message {i}", session_id)
        context_manager.add_assistant_message(f"Assistant message {i}", session_id)

    history = context_manager.get_history(session_id)
    assert len(history) == 8


def test_get_history_with_limit(context_manager):
    """Test getting history with limit"""
    session_id = context_manager.create_session()

    # Add messages
    for i in range(10):
        context_manager.add_user_message(f"Message {i}", session_id)

    # Get limited history
    history = context_manager.get_history(session_id, limit=5)
    assert len(history) == 5


def test_get_history_as_text(context_manager):
    """Test getting history as formatted text"""
    session_id = context_manager.create_session()

    context_manager.add_user_message("Hello", session_id)
    context_manager.add_assistant_message("Hi", session_id)

    # Without system labels
    text = context_manager.get_history_as_text(session_id, include_system=False)
    assert "Hello" in text
    assert "Hi" in text

    # With system labels
    text = context_manager.get_history_as_text(session_id, include_system=True)
    assert "User:" in text
    assert "Assistant:" in text


def test_get_context_for_prompt(context_manager):
    """Test getting context formatted for prompts"""
    session_id = context_manager.create_session()

    context_manager.add_user_message("Hello", session_id)
    context_manager.add_assistant_message("Hi", session_id)

    context = context_manager.get_context_for_prompt(session_id)
    assert "User:" in context
    assert "Assistant:" in context
    assert "Hello" in context
    assert "Hi" in context


def test_prune_history(context_manager):
    """Test automatic history pruning"""
    session_id = context_manager.create_session()

    # Add more messages than max_exchanges allows
    # max_exchanges = 5 means 10 messages (5 user + 5 assistant)
    for i in range(10):
        context_manager.add_user_message(f"User {i}", session_id)
        context_manager.add_assistant_message(f"Assistant {i}", session_id)

    # Should be pruned to 10 messages (5 exchanges)
    history = context_manager.get_history(session_id)
    assert len(history) <= 10


def test_clear_history(context_manager):
    """Test clearing conversation history"""
    session_id = context_manager.create_session()

    # Add messages
    context_manager.add_user_message("Hello", session_id)
    context_manager.add_assistant_message("Hi", session_id)

    # Clear history
    context_manager.clear_history(session_id)

    # Verify it's empty
    history = context_manager.get_history(session_id)
    assert len(history) == 0


def test_delete_session(context_manager):
    """Test deleting a session"""
    session_id = context_manager.create_session()

    context_manager.delete_session(session_id)

    assert session_id not in context_manager.sessions


def test_get_session_info(context_manager):
    """Test getting session information"""
    session_id = context_manager.create_session()

    context_manager.add_user_message("Test", session_id)

    info = context_manager.get_session_info(session_id)
    assert info is not None
    assert info["session_id"] == session_id
    assert info["message_count"] == 1


def test_list_sessions(context_manager):
    """Test listing all sessions"""
    # Create multiple sessions
    sid1 = context_manager.create_session()
    sid2 = context_manager.create_session()

    sessions = context_manager.list_sessions()
    assert len(sessions) >= 2
    assert sid1 in sessions
    assert sid2 in sessions


def test_get_exchange_count(context_manager):
    """Test counting exchanges"""
    session_id = context_manager.create_session()

    # Add 3 exchanges
    for i in range(3):
        context_manager.add_user_message(f"User {i}", session_id)
        context_manager.add_assistant_message(f"Assistant {i}", session_id)

    count = context_manager.get_exchange_count(session_id)
    assert count == 3


def test_multiple_sessions(context_manager):
    """Test managing multiple sessions independently"""
    # Create two sessions
    sid1 = context_manager.create_session()
    sid2 = context_manager.create_session()

    # Add different messages to each
    context_manager.add_user_message("Session 1 message", sid1)
    context_manager.add_user_message("Session 2 message", sid2)

    # Verify they're independent
    history1 = context_manager.get_history(sid1)
    history2 = context_manager.get_history(sid2)

    assert len(history1) == 1
    assert len(history2) == 1
    assert history1[0].content == "Session 1 message"
    assert history2[0].content == "Session 2 message"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
