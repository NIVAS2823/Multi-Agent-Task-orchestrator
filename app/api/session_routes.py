"""
Session API Routes

Manages conversation sessions with user authentication.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.session import SessionUpdate, SessionResponse, Session
from app.models.user import User  # NEW
from app.services.session_service import session_service
from app.api.dependencies import get_current_user  # NEW
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),  # NEW: Require auth
    limit: int = 50
):
    """
    List user's conversation sessions (PROTECTED)
    
    Returns only sessions belonging to the authenticated user
    """
    try:
        logger.info(f"📋 Listing sessions for user: {current_user.username}")
        
        # Get only user's sessions
        sessions = await session_service.list_sessions(
            user_id=str(current_user.id),  # NEW: Filter by user
            limit=limit
        )
        
        logger.info(f"✅ Retrieved {len(sessions)} sessions for {current_user.username}")
        return sessions
        
    except Exception as e:
        logger.error(f"❌ Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=Session)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user)  # NEW: Require auth
):
    """
    Get a specific session with all messages (PROTECTED)
    
    Only returns session if it belongs to the authenticated user
    """
    try:
        logger.info(f"📖 Fetching session: {session_id} for user: {current_user.username}")
        
        session = await session_service.get_session(session_id)
        
        if not session:
            logger.warning(f"⚠️ Session not found: {session_id}")
            raise HTTPException(
                status_code=404, 
                detail=f"Session not found: {session_id}"
            )
        
        # NEW: Verify session belongs to user
        if session.user_id != str(current_user.id):
            logger.warning(
                f"⚠️ User {current_user.username} attempted to access session {session_id} "
                f"owned by user {session.user_id}"
            )
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this session"
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
async def update_session(
    session_id: str,
    update_data: SessionUpdate,
    current_user: User = Depends(get_current_user)  # NEW: Require auth
):
    """
    Update session metadata (PROTECTED)
    
    Only allows updating sessions that belong to the authenticated user
    """
    try:
        logger.info(f"✏️ Updating session: {session_id} by user: {current_user.username}")
        
        # NEW: Verify ownership first
        session = await session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=404, 
                detail=f"Session not found: {session_id}"
            )
        
        if session.user_id != str(current_user.id):
            logger.warning(
                f"⚠️ User {current_user.username} attempted to update session {session_id} "
                f"owned by user {session.user_id}"
            )
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to update this session"
            )
        
        # Proceed with update
        success = await session_service.update_session(
            session_id=session_id,
            title=update_data.title
        )
        
        if not success:
            raise HTTPException(
                status_code=500, 
                detail="Failed to update session"
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
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user)  # NEW: Require auth
):
    """
    Delete a session (PROTECTED)
    
    Only allows deleting sessions that belong to the authenticated user
    """
    try:
        logger.info(f"🗑️ Deleting session: {session_id} by user: {current_user.username}")
        
        # NEW: Verify ownership first
        session = await session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=404, 
                detail=f"Session not found: {session_id}"
            )
        
        if session.user_id != str(current_user.id):
            logger.warning(
                f"⚠️ User {current_user.username} attempted to delete session {session_id} "
                f"owned by user {session.user_id}"
            )
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this session"
            )
        
        # Proceed with deletion
        success = await session_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=500, 
                detail="Failed to delete session"
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