"""
Session Service Module

This module provides business logic for managing conversation sessions.
It owns session lifecycle and guarantees Mongo-safe behavior.
"""

from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

from app.models.session import Session, Message, SessionResponse
from app.database.mongodb import get_database
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SessionService:
    def __init__(self):
        self.collection_name = "sessions"

    # ------------------------------------------------------------------
    # SESSION CREATION (Mongo owns IDs)
    # ------------------------------------------------------------------
    async def create_session(
        self,
        title: str = "New Conversation",
        user_id: Optional[str] = None,
    ) -> str:
        db = get_database()

        session = Session(
            title=title,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        result = await db[self.collection_name].insert_one(
            session.dict(by_alias=True, exclude={"id"})
        )

        session_id = str(result.inserted_id)
        logger.info(f"✅ Created new session {session_id}")
        return session_id

    # ------------------------------------------------------------------
    # INTERNAL: SAFE OBJECTID
    # ------------------------------------------------------------------
    def _safe_object_id(self, value: Optional[str]) -> Optional[ObjectId]:
        if not value:
            return None
        try:
            return ObjectId(value)
        except (InvalidId, TypeError):
            return None

    # ------------------------------------------------------------------
    # ADD MESSAGE (AUTO-CREATE SESSION IF NEEDED)
    # ------------------------------------------------------------------
    async def add_message(
        self,
        session_id: Optional[str],
        role: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Add a message to a session.
        If session_id is invalid or missing, a new session is created.

        Returns:
            str: session_id used
        """
        db = get_database()

        oid = self._safe_object_id(session_id)

        # 🔥 Auto-create session if ID invalid or missing
        if oid is None:
            session_id = await self.create_session()
            oid = ObjectId(session_id)
            logger.info(f"🆕 Auto-created session {session_id}")

        message = Message(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata,
        )

        await db[self.collection_name].update_one(
            {"_id": oid},
            {
                "$push": {"messages": message.dict()},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )

        logger.info(
            f"💬 Added {role} message to session {oid} "
            f"(chars={len(content)})"
        )

        return str(oid)

    # ------------------------------------------------------------------
    # GET SESSION
    # ------------------------------------------------------------------
    async def get_session(self, session_id: str) -> Optional[Session]:
        db = get_database()

        try:
            session_data = await db[self.collection_name].find_one(
                {"_id": ObjectId(session_id)}
            )

            if not session_data:
                logger.warning(f"⚠️ Session not found: {session_id}")
                return None

        # 🔥 CRITICAL FIX
            session_data["_id"] = str(session_data["_id"])

            logger.info(f"📖 Retrieved session: {session_id}")
            return Session(**session_data)

        except Exception as e:
            logger.error(f"❌ Error getting session {session_id}: {str(e)}")
            return None


    # ------------------------------------------------------------------
    # LIST SESSIONS
    # ------------------------------------------------------------------
    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[SessionResponse]:
        db = get_database()

        query = {}
        if user_id:
            query["user_id"] = user_id

        cursor = (
            db[self.collection_name]
            .find(query)
            .sort("updated_at", -1)
            .limit(limit)
        )

        sessions = await cursor.to_list(length=limit)
        result = []

        for s in sessions:
            messages = s.get("messages", [])
            result.append(
                SessionResponse(
                    id=str(s["_id"]),
                    title=s.get("title", "New Conversation"),
                    created_at=s.get("created_at"),
                    updated_at=s.get("updated_at"),
                    message_count=len(messages),
                    last_message=messages[-1]["content"] if messages else None,
                )
            )

        return result

    # ------------------------------------------------------------------
    # DELETE SESSION
    # ------------------------------------------------------------------
    async def delete_session(self, session_id: str) -> bool:
        db = get_database()
        oid = self._safe_object_id(session_id)

        if oid is None:
            return False

        result = await db[self.collection_name].delete_one({"_id": oid})
        return result.deleted_count > 0

    # ------------------------------------------------------------------
    # GET SESSION MESSAGES
    # ------------------------------------------------------------------
    async def get_session_messages(self, session_id: str) -> List[Message]:
        session = await self.get_session(session_id)
        return session.messages if session else []


# Singleton
session_service = SessionService()
