"""
Authentication Routes

Handles user registration, login, and Google OAuth.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
import httpx
import os
from typing import Optional

from app.models.user import UserCreate, UserLogin, Token, UserResponse, User
from app.services.user_service import user_service
from app.utils.security import create_access_token, validate_password_strength
from app.api.dependencies import get_current_user
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://multi-agent-task-orchestrator-production.up.railway.app/api/auth/google/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user with username/password
    
    Password requirements:
    - At least 8 characters
    - Contains uppercase and lowercase letters
    - Contains at least one digit
    """
    try:
        logger.info(f"📝 Registration attempt: {user_data.username}")
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(user_data.password)
        if not is_valid:
            logger.warning(f"⚠️ Weak password for {user_data.username}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Create user
        user_id = await user_service.create_user(user_data)
        
        if not user_id:
            logger.warning(f"⚠️ Failed to create user: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Get the created user
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User created but could not be retrieved"
            )
        
        # Create JWT token
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "username": user.username
        }
        access_token = create_access_token(token_data)
        
        # Convert to response format
        user_response = user_service.user_to_response(user)
        
        logger.info(f"✅ User registered successfully: {user.username}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login with username/email and password
    
    Returns JWT token valid for 24 hours
    """
    try:
        logger.info(f"🔐 Login attempt: {credentials.username}")
        
        # Authenticate user
        user = await user_service.authenticate_user(
            credentials.username,
            credentials.password
        )
        
        if not user:
            logger.warning(f"⚠️ Failed login attempt: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create JWT token
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "username": user.username
        }
        access_token = create_access_token(token_data)
        
        # Convert to response format
        user_response = user_service.user_to_response(user)
        
        logger.info(f"✅ User logged in: {user.username}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires valid JWT token in Authorization header
    """
    logger.debug(f"📋 User info requested: {current_user.username}")
    return user_service.user_to_response(current_user)


@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth login flow
    
    Redirects to Google's OAuth consent screen
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    # Google OAuth URL
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    logger.info("🔗 Google OAuth initiated")
    return {"url": google_auth_url}


@router.get("/google/callback")
async def google_callback(code: str, error: Optional[str] = None):
    """
    Handle Google OAuth callback
    
    Exchanges authorization code for user info and creates/updates user
    """
    if error:
        logger.error(f"❌ Google OAuth error: {error}")
        return RedirectResponse(url=f"{FRONTEND_URL}?error=google_auth_failed")
    
    if not code:
        logger.error("❌ No authorization code received")
        return RedirectResponse(url=f"{FRONTEND_URL}?error=no_code")
    
    try:
        logger.info("🔄 Processing Google OAuth callback")
        
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            
            if token_response.status_code != 200:
                logger.error(f"❌ Token exchange failed: {token_response.text}")
                return RedirectResponse(url=f"{FRONTEND_URL}?error=token_exchange_failed")
            
            tokens = token_response.json()
            access_token_google = tokens.get("access_token")
            
            # Get user info from Google
            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token_google}"},
            )
            
            if user_info_response.status_code != 200:
                logger.error("❌ Failed to get user info from Google")
                return RedirectResponse(url=f"{FRONTEND_URL}?error=userinfo_failed")
            
            user_info = user_info_response.json()
        
        # Extract user data
        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")
        
        if not google_id or not email:
            logger.error("❌ Incomplete user info from Google")
            return RedirectResponse(url=f"{FRONTEND_URL}?error=incomplete_userinfo")
        
        # Create or update user
        user_id = await user_service.create_or_update_google_user(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture
        )
        
        if not user_id:
            logger.error("❌ Failed to create/update Google user")
            return RedirectResponse(url=f"{FRONTEND_URL}?error=user_creation_failed")
        
        # Get user
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            logger.error("❌ User created but not found")
            return RedirectResponse(url=f"{FRONTEND_URL}?error=user_not_found")
        
        # Create our JWT token
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "username": user.username
        }
        jwt_token = create_access_token(token_data)
        
        logger.info(f"✅ Google OAuth successful: {email}")
        
        # Redirect to frontend with token
        return RedirectResponse(url=f"{FRONTEND_URL}?token={jwt_token}")
        
    except Exception as e:
        logger.error(f"❌ Google OAuth callback error: {str(e)}")
        return RedirectResponse(url=f"{FRONTEND_URL}?error=oauth_failed")