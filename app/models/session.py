"""
Session and Message Data Models
"""

from pydantic import BaseModel, Field, GetJsonSchemaHandler
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema


# -------------------------------------------------------------------
# Mongo ObjectId wrapper for Pydantic v2
# -------------------------------------------------------------------
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler
    ) -> core_schema.CoreSchema:
        return core_schema.str_schema()

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ):
        json_schema = handler(core_schema)
        json_schema.update(
            type="string",
            example="507f1f77bcf86cd799439011"
        )
        return json_schema


# -------------------------------------------------------------------
# Message model
# -------------------------------------------------------------------
class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Analyze sales data from Q4",
                "timestamp": "2024-01-15T10:30:00",
                "metadata": {}
            }
        }


# -------------------------------------------------------------------
# Session model (Mongo-backed)
# -------------------------------------------------------------------
class Session(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = "New Conversation"
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "title": "Sales Analysis Discussion",
                "messages": [
                    {
                        "role": "user",
                        "content": "Analyze Q4 sales data",
                        "timestamp": "2024-01-15T10:30:00"
                    }
                ],
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:35:00"
            }
        }


# -------------------------------------------------------------------
# API DTOs (optional / future-facing)
# -------------------------------------------------------------------
class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    user_id: Optional[str] = None


class SessionUpdate(BaseModel):
    title: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message: Optional[str] = None


class MessageCreate(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
