"""
User Features Database Module

Manages storage and retrieval of user biometric features:
- Face encodings
- Voice embeddings
- User metadata

Uses SQLite with SQLAlchemy ORM for async database operations.
"""

import pickle
from datetime import datetime
from typing import Optional, List, Dict, Any
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary, Float
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, Session
from loguru import logger

Base = declarative_base()


class User(Base):
    """User model storing biometric features and metadata"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Face recognition data
    face_encoding = Column(LargeBinary, nullable=True)  # Pickled numpy array
    face_confidence = Column(Float, default=0.0)

    # Voice biometrics data
    voice_embedding = Column(LargeBinary, nullable=True)  # Pickled numpy array
    voice_confidence = Column(Float, default=0.0)

    # Metadata
    language_preference = Column(String(10), default='en')
    last_seen = Column(DateTime, default=datetime.utcnow)
    recognition_count = Column(Integer, default=0)


class UserFeaturesDB:
    """
    Database manager for user biometric features.

    Provides async and sync interfaces for storing and retrieving
    face encodings, voice embeddings, and user metadata.
    """

    def __init__(self, db_path: str = "shared/user_data.db", async_mode: bool = True):
        """
        Initialize the user features database.

        Args:
            db_path: Path to SQLite database file
            async_mode: Use async database operations
        """
        self.db_path = db_path
        self.async_mode = async_mode

        if async_mode:
            self.engine = create_async_engine(
                f"sqlite+aiosqlite:///{db_path}",
                echo=False,
                future=True
            )
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        else:
            self.engine = create_engine(
                f"sqlite:///{db_path}",
                echo=False
            )

        logger.info(f"UserFeaturesDB initialized with path: {db_path}, async={async_mode}")

    async def initialize_async(self):
        """Initialize database tables (async)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully (async)")

    def initialize_sync(self):
        """Initialize database tables (sync)"""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully (sync)")

    # Async methods
    async def add_user_async(
        self,
        name: str,
        face_encoding: Optional[np.ndarray] = None,
        voice_embedding: Optional[np.ndarray] = None,
        language_preference: str = 'en'
    ) -> int:
        """
        Add a new user to the database (async).

        Args:
            name: User's name
            face_encoding: Face encoding as numpy array
            voice_embedding: Voice embedding as numpy array
            language_preference: Preferred language (en/ru)

        Returns:
            User ID of the created user
        """
        async with self.async_session_maker() as session:
            # Check if user already exists
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.name == name))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                logger.warning(f"User {name} already exists")
                return existing_user.id

            # Create new user
            user = User(
                name=name,
                face_encoding=pickle.dumps(face_encoding) if face_encoding is not None else None,
                voice_embedding=pickle.dumps(voice_embedding) if voice_embedding is not None else None,
                language_preference=language_preference
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

            logger.info(f"Added new user: {name} (ID: {user.id})")
            return user.id

    async def update_user_face_async(
        self,
        user_id: int,
        face_encoding: np.ndarray,
        confidence: float = 1.0
    ) -> bool:
        """
        Update user's face encoding (async).

        Args:
            user_id: User ID
            face_encoding: New face encoding
            confidence: Confidence score

        Returns:
            True if updated successfully
        """
        async with self.async_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                logger.error(f"User ID {user_id} not found")
                return False

            user.face_encoding = pickle.dumps(face_encoding)
            user.face_confidence = confidence
            user.updated_at = datetime.utcnow()

            await session.commit()
            logger.info(f"Updated face encoding for user {user.name}")
            return True

    async def update_user_voice_async(
        self,
        user_id: int,
        voice_embedding: np.ndarray,
        confidence: float = 1.0
    ) -> bool:
        """
        Update user's voice embedding (async).

        Args:
            user_id: User ID
            voice_embedding: New voice embedding
            confidence: Confidence score

        Returns:
            True if updated successfully
        """
        async with self.async_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                logger.error(f"User ID {user_id} not found")
                return False

            user.voice_embedding = pickle.dumps(voice_embedding)
            user.voice_confidence = confidence
            user.updated_at = datetime.utcnow()

            await session.commit()
            logger.info(f"Updated voice embedding for user {user.name}")
            return True

    async def get_user_by_id_async(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID (async)"""
        async with self.async_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return None

            return self._user_to_dict(user)

    async def get_user_by_name_async(self, name: str) -> Optional[Dict[str, Any]]:
        """Get user by name (async)"""
        async with self.async_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.name == name))
            user = result.scalar_one_or_none()

            if not user:
                return None

            return self._user_to_dict(user)

    async def get_all_users_async(self) -> List[Dict[str, Any]]:
        """Get all users (async)"""
        async with self.async_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(User))
            users = result.scalars().all()

            return [self._user_to_dict(user) for user in users]

    async def get_all_face_encodings_async(self) -> Dict[int, np.ndarray]:
        """
        Get all face encodings for recognition (async).

        Returns:
            Dictionary mapping user_id to face encoding
        """
        async with self.async_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.face_encoding.isnot(None))
            )
            users = result.scalars().all()

            encodings = {}
            for user in users:
                encodings[user.id] = pickle.loads(user.face_encoding)

            return encodings

    async def get_all_voice_embeddings_async(self) -> Dict[int, np.ndarray]:
        """
        Get all voice embeddings for recognition (async).

        Returns:
            Dictionary mapping user_id to voice embedding
        """
        async with self.async_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.voice_embedding.isnot(None))
            )
            users = result.scalars().all()

            embeddings = {}
            for user in users:
                embeddings[user.id] = pickle.loads(user.voice_embedding)

            return embeddings

    async def update_last_seen_async(self, user_id: int) -> bool:
        """Update user's last seen timestamp (async)"""
        async with self.async_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return False

            user.last_seen = datetime.utcnow()
            user.recognition_count += 1

            await session.commit()
            return True

    async def delete_user_async(self, user_id: int) -> bool:
        """Delete user by ID (async)"""
        async with self.async_session_maker() as session:
            from sqlalchemy import select, delete
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(f"User ID {user_id} not found for deletion")
                return False

            await session.execute(delete(User).where(User.id == user_id))
            await session.commit()

            logger.info(f"Deleted user ID {user_id}")
            return True

    # Synchronous methods (for backward compatibility)
    def add_user_sync(
        self,
        name: str,
        face_encoding: Optional[np.ndarray] = None,
        voice_embedding: Optional[np.ndarray] = None,
        language_preference: str = 'en'
    ) -> int:
        """Add a new user to the database (sync)"""
        with Session(self.engine) as session:
            # Check if user already exists
            existing_user = session.query(User).filter(User.name == name).first()

            if existing_user:
                logger.warning(f"User {name} already exists")
                return existing_user.id

            # Create new user
            user = User(
                name=name,
                face_encoding=pickle.dumps(face_encoding) if face_encoding is not None else None,
                voice_embedding=pickle.dumps(voice_embedding) if voice_embedding is not None else None,
                language_preference=language_preference
            )

            session.add(user)
            session.commit()
            session.refresh(user)

            logger.info(f"Added new user: {name} (ID: {user.id})")
            return user.id

    def get_all_users_sync(self) -> List[Dict[str, Any]]:
        """Get all users (sync)"""
        with Session(self.engine) as session:
            users = session.query(User).all()
            return [self._user_to_dict(user) for user in users]

    # Utility methods
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert User model to dictionary"""
        return {
            'id': user.id,
            'name': user.name,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'face_encoding': pickle.loads(user.face_encoding) if user.face_encoding else None,
            'face_confidence': user.face_confidence,
            'voice_embedding': pickle.loads(user.voice_embedding) if user.voice_embedding else None,
            'voice_confidence': user.voice_confidence,
            'language_preference': user.language_preference,
            'last_seen': user.last_seen.isoformat() if user.last_seen else None,
            'recognition_count': user.recognition_count
        }

    async def close_async(self):
        """Close async database connection"""
        await self.engine.dispose()
        logger.info("Database connection closed (async)")

    def close_sync(self):
        """Close sync database connection"""
        self.engine.dispose()
        logger.info("Database connection closed (sync)")
