# Models package initialization
# Import all models for easy access

# Session models
from app.models.session import (
    Message,
    Session,
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    MessageCreate,
    PyObjectId as SessionPyObjectId
)

# User models (NEW)
from app.models.user import (
    User,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenData,
    PyObjectId as UserPyObjectId
)

__all__ = [
    # Session models
    "Message",
    "Session",
    "SessionCreate",
    "SessionUpdate",
    "SessionResponse",
    "MessageCreate",
    "SessionPyObjectId",
    
    # User models
    "User",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    "UserPyObjectId",
]