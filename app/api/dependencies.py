"""
Authentication Dependencies

FastAPI dependencies for protecting routes with JWT authentication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.models.user import User
from app.services.user_service import user_service
from app.utils.security import verify_token
from app.utils.logger import get_logger

logger = get_logger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token
    
    This is used to protect routes that require authentication.
    Add it as a dependency: user: User = Depends(get_current_user)
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    
    # Extract token
    token = credentials.credentials
    
    # Verify and decode token
    payload = verify_token(token)
    
    if not payload:
        logger.warning("⚠️ Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user_id from token
    user_id: str = payload.get("user_id")
    
    if not user_id:
        logger.warning("⚠️ Token missing user_id")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        logger.warning(f"⚠️ User not found for token: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"⚠️ Inactive user attempted access: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    logger.debug(f"✅ Authenticated user: {user.username}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user (additional check)
    
    Use this if you want to be extra explicit about checking active status.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[User]:
    """
    Dependency to optionally get current user (for public endpoints that want user context)
    
    Returns None if no token provided or token is invalid.
    Does not raise exceptions.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        user = await user_service.get_user_by_id(user_id)
        return user if user and user.is_active else None
        
    except Exception as e:
        logger.debug(f"Optional auth failed: {str(e)}")
        return None