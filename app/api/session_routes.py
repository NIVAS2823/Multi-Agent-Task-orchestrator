"""
Session API Routes

This module provides RESTful API endpoints for managing conversation sessions:
- POST /sessions/ - Create a new session
- GET /sessions/ - List all sessions
- GET /sessions/{id} - Get specific session with messages
- PATCH /sessions/{id} - Update session metadata
- DELETE /sessions/{id} - Delete a session
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.session import (
    SessionCreate, 
    SessionUpdate, 
    SessionResponse, 
    Session
)
from app.services.session_service import session_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create router with prefix and tags
router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/", response_model=dict, status_code=201)
async def create_session(session_data: SessionCreate):
    """
    Create a new conversation session
    
    Args:
        session_data: Session creation data (title, user_id)
        
    Returns:
        dict: Contains session_id and success message
        
    Example:
        POST /api/sessions/
        {
            "title": "My AI Assistant Session",
            "user_id": "user123"
        }
        
        Response:
        {
            "session_id": "507f1f77bcf86cd799439011",
            "message": "Session created successfully"
        }
    """
    try:
        logger.info(f"📝 Creating new session: '{session_data.title}'")
        
        session_id = await session_service.create_session(
            title=session_data.title,
            user_id=session_data.user_id
        )
        
        return {
            "session_id": session_id, 
            "message": "Session created successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of sessions")
):
    """
    List all conversation sessions
    
    Args:
        user_id: Optional filter by user ID
        limit: Maximum number of sessions to return (1-100, default: 50)
        
    Returns:
        List of SessionResponse objects with session summaries
        
    Example:
        GET /api/sessions/?limit=10
        
        Response:
        [
            {
                "id": "507f1f77bcf86cd799439011",
                "title": "Sales Analysis Discussion",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:35:00",
                "message_count": 4,
                "last_message": "Here's the analysis..."
            }
        ]
    """
    try:
        logger.info(f"📋 Listing sessions (user_id={user_id}, limit={limit})")
        
        sessions = await session_service.list_sessions(
            user_id=user_id, 
            limit=limit
        )
        
        logger.info(f"✅ Retrieved {len(sessions)} sessions")
        return sessions
        
    except Exception as e:
        logger.error(f"❌ Error listing sessions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """
    Get a specific session with all messages
    
    Args:
        session_id: The session identifier
        
    Returns:
        Complete Session object with all messages
        
    Raises:
        404: If session not found
        
    Example:
        GET /api/sessions/507f1f77bcf86cd799439011
        
        Response:
        {
            "id": "507f1f77bcf86cd799439011",
            "title": "Sales Analysis Discussion",
            "messages": [
                {
                    "role": "user",
                    "content": "Analyze Q4 sales",
                    "timestamp": "2024-01-15T10:30:00"
                },
                {
                    "role": "assistant",
                    "content": "Here's the analysis...",
                    "timestamp": "2024-01-15T10:32:00"
                }
            ],
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-15T10:35:00"
        }
    """
    try:
        logger.info(f"📖 Fetching session: {session_id}")
        
        session = await session_service.get_session(session_id)
        
        if not session:
            logger.warning(f"⚠️ Session not found: {session_id}")
            raise HTTPException(
                status_code=404, 
                detail=f"Session not found: {session_id}"
            )
        
        logger.info(
            f"✅ Retrieved session with {len(session.messages)} messages"
        )
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"❌ Error getting session {session_id}: {str(e)}", 
            exc_info=True
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get session: {str(e)}"
        )


@router.patch("/{session_id}", response_model=dict)
async def update_session(session_id: str, update_data: SessionUpdate):
    """
    Update session metadata (e.g., title)
    
    Args:
        session_id: The session to update
        update_data: Fields to update (currently only title)
        
    Returns:
        Success message
        
    Raises:
        404: If session not found
        
    Example:
        PATCH /api/sessions/507f1f77bcf86cd799439011
        {
            "title": "Updated Session Title"
        }
        
        Response:
        {
            "message": "Session updated successfully"
        }
    """
    try:
        logger.info(f"✏️ Updating session: {session_id}")
        
        success = await session_service.update_session(
            session_id=session_id,
            title=update_data.title
        )
        
        if not success:
            logger.warning(f"⚠️ Session not found for update: {session_id}")
            raise HTTPException(
                status_code=404, 
                detail=f"Session not found: {session_id}"
            )
        
        logger.info(f"✅ Session updated successfully: {session_id}")
        return {"message": "Session updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"❌ Error updating session {session_id}: {str(e)}", 
            exc_info=True
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to update session: {str(e)}"
        )


@router.delete("/{session_id}", response_model=dict)
async def delete_session(session_id: str):
    """
    Delete a session permanently
    
    Args:
        session_id: The session to delete
        
    Returns:
        Success message
        
    Raises:
        404: If session not found
        
    Warning:
        This operation is permanent and cannot be undone!
        
    Example:
        DELETE /api/sessions/507f1f77bcf86cd799439011
        
        Response:
        {
            "message": "Session deleted successfully"
        }
    """
    try:
        logger.info(f"🗑️ Deleting session: {session_id}")
        
        success = await session_service.delete_session(session_id)
        
        if not success:
            logger.warning(f"⚠️ Session not found for deletion: {session_id}")
            raise HTTPException(
                status_code=404, 
                detail=f"Session not found: {session_id}"
            )
        
        logger.info(f"✅ Session deleted successfully: {session_id}")
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"❌ Error deleting session {session_id}: {str(e)}", 
            exc_info=True
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete session: {str(e)}"
        )