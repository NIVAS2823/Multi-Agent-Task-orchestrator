"""
User Model

Pydantic v2 models for user authentication and management.
Compatible with MongoDB ObjectId.
"""

from typing import Optional
from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr
from pydantic_core import core_schema


# =========================
# Custom Mongo ObjectId
# =========================

class PyObjectId(ObjectId):
    """Pydantic v2 compatible ObjectId"""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, value):
        if isinstance(value, ObjectId):
            return value
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        schema.update(type="string")


# =========================
# Database Model
# =========================

class User(BaseModel):
    """
    User model stored in MongoDB.

    Supports:
    - Traditional auth (username/password)
    - OAuth (Google)
    """

    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    email: EmailStr
    username: str
    full_name: Optional[str] = None

    # Auth
    hashed_password: Optional[str] = None  # None for OAuth users

    # OAuth
    google_id: Optional[str] = None
    profile_picture: Optional[str] = None

    # Metadata
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }


# =========================
# Request Models
# =========================

class UserCreate(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Request model for user login"""
    username: str  # username or email
    password: str


# =========================
# Response Models
# =========================

class UserResponse(BaseModel):
    """Safe user response (no secrets)"""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Data stored inside JWT"""
    user_id: str
    email: str
    username: str
