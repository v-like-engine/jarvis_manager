"""
Context Manager - Manage conversation history and context

Handles:
- Storing conversation history
- Managing context window (last N exchanges)
- Token counting and context truncation
- Session management
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A single message in the conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationSession:
    """A conversation session with history"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """Manages conversation context and history"""

    def __init__(self, max_exchanges: int = 5, max_tokens_per_exchange: int = 200):
        """
        Initialize ContextManager

        Args:
            max_exchanges: Maximum number of exchanges (user + assistant pairs) to keep
            max_tokens_per_exchange: Maximum tokens per exchange for truncation
        """
        self.max_exchanges = max_exchanges
        self.max_tokens_per_exchange = max_tokens_per_exchange

        # Store sessions by session_id
        self.sessions: Dict[str, ConversationSession] = {}

        # Current active session
        self.current_session_id: Optional[str] = None

        logger.info(
            f"ContextManager initialized (max_exchanges={max_exchanges}, "
            f"max_tokens={max_tokens_per_exchange})"
        )

    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new conversation session

        Args:
            metadata: Optional metadata for the session

        Returns:
            Session ID
        """
        session = ConversationSession(metadata=metadata or {})
        self.sessions[session.session_id] = session
        self.current_session_id = session.session_id

        logger.info(f"Created new session: {session.session_id}")
        return session.session_id

    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """
        Get existing session or create new one

        Args:
            session_id: Optional session ID

        Returns:
            Session ID
        """
        if session_id and session_id in self.sessions:
            self.current_session_id = session_id
            return session_id

        return self.create_session()

    def add_message(
        self,
        role: str,
        content: str,
        session_id: Optional[str] = None,
        tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a message to the conversation history

        Args:
            role: "user" or "assistant"
            content: Message content
            session_id: Optional session ID (uses current if not provided)
            tokens: Optional token count (will estimate if not provided)
            metadata: Optional message metadata
        """
        # Get or create session
        sid = self.get_or_create_session(session_id)
        session = self.sessions[sid]

        # Estimate tokens if not provided (rough approximation)
        if tokens is None:
            tokens = len(content) // 4

        # Create message
        message = Message(
            role=role,
            content=content,
            tokens=tokens,
            metadata=metadata or {},
        )

        # Add to session
        session.messages.append(message)
        session.last_activity = datetime.now()

        logger.debug(
            f"Added {role} message to session {sid} ({tokens} tokens): "
            f"{content[:50]}..."
        )

        # Prune old messages if needed
        self._prune_history(sid)

    def add_user_message(
        self,
        content: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Add a user message to history"""
        self.add_message("user", content, session_id, metadata=metadata)

    def add_assistant_message(
        self,
        content: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Add an assistant message to history"""
        self.add_message("assistant", content, session_id, metadata=metadata)

    def get_history(
        self,
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """
        Get conversation history

        Args:
            session_id: Optional session ID (uses current if not provided)
            limit: Optional limit on number of messages

        Returns:
            List of messages
        """
        sid = session_id or self.current_session_id

        if not sid or sid not in self.sessions:
            return []

        messages = self.sessions[sid].messages

        if limit:
            messages = messages[-limit:]

        return messages

    def get_history_as_text(
        self,
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
        include_system: bool = False,
    ) -> str:
        """
        Get conversation history as formatted text

        Args:
            session_id: Optional session ID
            limit: Optional limit on number of messages
            include_system: Include system role labels

        Returns:
            Formatted history text
        """
        messages = self.get_history(session_id, limit)

        if not messages:
            return ""

        lines = []
        for msg in messages:
            if include_system:
                role_label = "User" if msg.role == "user" else "Assistant"
                lines.append(f"{role_label}: {msg.content}")
            else:
                lines.append(msg.content)

        return "\n".join(lines)

    def get_context_for_prompt(
        self,
        session_id: Optional[str] = None,
        max_exchanges: Optional[int] = None,
    ) -> str:
        """
        Get context formatted for inclusion in a prompt

        Args:
            session_id: Optional session ID
            max_exchanges: Maximum exchanges to include (overrides default)

        Returns:
            Formatted context for prompt
        """
        limit = (max_exchanges or self.max_exchanges) * 2  # user + assistant = 1 exchange

        messages = self.get_history(session_id, limit)

        if not messages:
            return ""

        # Format as conversation
        context_parts = []
        for msg in messages:
            role = "User" if msg.role == "user" else "Assistant"
            context_parts.append(f"{role}: {msg.content}")

        return "\n".join(context_parts)

    def _prune_history(self, session_id: str):
        """
        Prune conversation history to stay within limits

        Args:
            session_id: Session to prune
        """
        session = self.sessions.get(session_id)
        if not session:
            return

        max_messages = self.max_exchanges * 2  # user + assistant pairs

        if len(session.messages) > max_messages:
            # Keep only the most recent messages
            removed = len(session.messages) - max_messages
            session.messages = session.messages[-max_messages:]
            logger.debug(f"Pruned {removed} old messages from session {session_id}")

    def clear_history(self, session_id: Optional[str] = None):
        """
        Clear conversation history

        Args:
            session_id: Optional session ID (clears current if not provided)
        """
        sid = session_id or self.current_session_id

        if not sid or sid not in self.sessions:
            logger.warning(f"No session to clear: {sid}")
            return

        self.sessions[sid].messages.clear()
        logger.info(f"Cleared history for session: {sid}")

    def delete_session(self, session_id: str):
        """
        Delete a session

        Args:
            session_id: Session to delete
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")

            if self.current_session_id == session_id:
                self.current_session_id = None
        else:
            logger.warning(f"Session not found: {session_id}")

    def get_session_info(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a session

        Args:
            session_id: Optional session ID

        Returns:
            Session information
        """
        sid = session_id or self.current_session_id

        if not sid or sid not in self.sessions:
            return {"error": "Session not found"}

        session = self.sessions[sid]

        return {
            "session_id": session.session_id,
            "message_count": len(session.messages),
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "metadata": session.metadata,
        }

    def list_sessions(self) -> List[str]:
        """
        List all session IDs

        Returns:
            List of session IDs
        """
        return list(self.sessions.keys())

    def get_total_tokens(self, session_id: Optional[str] = None) -> int:
        """
        Get total token count for a session

        Args:
            session_id: Optional session ID

        Returns:
            Total tokens in session
        """
        messages = self.get_history(session_id)
        return sum(msg.tokens for msg in messages)

    def get_exchange_count(self, session_id: Optional[str] = None) -> int:
        """
        Get number of exchanges (user + assistant pairs) in session

        Args:
            session_id: Optional session ID

        Returns:
            Number of exchanges
        """
        messages = self.get_history(session_id)
        # Count pairs of user/assistant messages
        return len(messages) // 2


if __name__ == "__main__":
    # Test the context manager
    logging.basicConfig(level=logging.INFO)

    manager = ContextManager(max_exchanges=5)

    # Create a session
    session_id = manager.create_session()
    print(f"Created session: {session_id}")

    # Add some messages
    manager.add_user_message("Hello!")
    manager.add_assistant_message("Gerald at your service.")
    manager.add_user_message("What can you do?")
    manager.add_assistant_message("I can help you manage your system.")

    # Get history
    print("\nConversation history:")
    print(manager.get_context_for_prompt())

    # Session info
    print("\nSession info:")
    print(manager.get_session_info())
