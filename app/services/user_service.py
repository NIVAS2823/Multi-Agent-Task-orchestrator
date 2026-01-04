"""
User Service

Handles user CRUD operations and authentication logic.
"""

from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.models.user import User, UserCreate, UserResponse
from app.database.mongodb import get_database
from app.utils.security import get_password_hash, verify_password
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for managing users"""
    
    def __init__(self):
        self.collection_name = "users"
    
    async def create_user(self, user_data: UserCreate) -> Optional[str]:
        """
        Create a new user with username/password
        
        Args:
            user_data: User registration data
            
        Returns:
            str: User ID if successful, None otherwise
        """
        db = get_database()
        
        try:
            # Check if user already exists
            existing_user = await db[self.collection_name].find_one({
                "$or": [
                    {"email": user_data.email},
                    {"username": user_data.username}
                ]
            })
            
            if existing_user:
                if existing_user.get("email") == user_data.email:
                    logger.warning(f"⚠️ Email already registered: {user_data.email}")
                    return None
                if existing_user.get("username") == user_data.username:
                    logger.warning(f"⚠️ Username already taken: {user_data.username}")
                    return None
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)

            logger.error(
    f"[DEBUG] password value = {user_data.password!r}, "
    f"byte_length = {len(user_data.password.encode('utf-8'))}"
)
            
            # Create user document
            user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True,
                is_verified=False  # Email verification can be added later
            )
            
            # Insert into database
            result = await db[self.collection_name].insert_one(
                user.dict(by_alias=True, exclude={"id"})
            )
            
            user_id = str(result.inserted_id)
            logger.info(f"✅ Created user: {user_data.username} (ID: {user_id})")
            return user_id
            
        except Exception as e:
            logger.error(f"❌ Error creating user: {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        db = get_database()
        
        try:
            user_data = await db[self.collection_name].find_one(
                {"_id": ObjectId(user_id)}
            )
            
            if user_data:
                user_data["id"] = str(user_data["_id"])
                return User(**user_data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting user by ID {user_id}: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        db = get_database()
        
        try:
            user_data = await db[self.collection_name].find_one({"email": email})
            
            if user_data:
                user_data["id"] = str(user_data["_id"])
                return User(**user_data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting user by email: {str(e)}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        db = get_database()
        
        try:
            user_data = await db[self.collection_name].find_one({"username": username})
            
            if user_data:
                user_data["id"] = str(user_data["_id"])
                return User(**user_data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting user by username: {str(e)}")
            return None
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username/email and password
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            User object if authenticated, None otherwise
        """
        try:
            # Try to find by username first, then email
            user = await self.get_user_by_username(username)
            if not user:
                user = await self.get_user_by_email(username)
            
            if not user:
                logger.warning(f"⚠️ User not found: {username}")
                return None
            
            # Check if user has a password (OAuth users don't)
            if not user.hashed_password:
                logger.warning(f"⚠️ User {username} registered via OAuth, cannot use password")
                return None
            
            # Verify password
            if not verify_password(password, user.hashed_password):
                logger.warning(f"⚠️ Invalid password for user: {username}")
                return None
            
            # Update last login
            await self.update_last_login(str(user.id))
            
            logger.info(f"✅ User authenticated: {username}")
            return user
            
        except Exception as e:
            logger.error(f"❌ Error authenticating user: {str(e)}")
            return None
    
    async def create_or_update_google_user(
        self,
        google_id: str,
        email: str,
        name: str,
        picture: Optional[str] = None
    ) -> Optional[str]:
        """
        Create or update user from Google OAuth
        
        Args:
            google_id: Google user ID
            email: User email
            name: User full name
            picture: Profile picture URL
            
        Returns:
            str: User ID
        """
        db = get_database()
        
        try:
            # Check if user exists by google_id
            user_data = await db[self.collection_name].find_one({"google_id": google_id})
            
            if user_data:
                # Update existing user
                user_id = str(user_data["_id"])
                await db[self.collection_name].update_one(
                    {"_id": ObjectId(user_id)},
                    {
                        "$set": {
                            "full_name": name,
                            "profile_picture": picture,
                            "updated_at": datetime.utcnow(),
                            "last_login": datetime.utcnow()
                        }
                    }
                )
                logger.info(f"✅ Updated Google user: {email}")
                return user_id
            
            # Check if email already exists (user might have registered with password)
            user_data = await db[self.collection_name].find_one({"email": email})
            
            if user_data:
                # Link Google account to existing user
                user_id = str(user_data["_id"])
                await db[self.collection_name].update_one(
                    {"_id": ObjectId(user_id)},
                    {
                        "$set": {
                            "google_id": google_id,
                            "profile_picture": picture,
                            "is_verified": True,  # Google users are verified
                            "updated_at": datetime.utcnow(),
                            "last_login": datetime.utcnow()
                        }
                    }
                )
                logger.info(f"✅ Linked Google account to existing user: {email}")
                return user_id
            
            # Create new user
            # Generate unique username from email
            username = email.split("@")[0]
            base_username = username
            counter = 1
            
            while await self.get_user_by_username(username):
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User(
                email=email,
                username=username,
                full_name=name,
                google_id=google_id,
                profile_picture=picture,
                is_active=True,
                is_verified=True,  # Google users are auto-verified
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            
            result = await db[self.collection_name].insert_one(
                user.dict(by_alias=True, exclude={"id"})
            )
            
            user_id = str(result.inserted_id)
            logger.info(f"✅ Created new Google user: {email} (ID: {user_id})")
            return user_id
            
        except Exception as e:
            logger.error(f"❌ Error creating/updating Google user: {str(e)}")
            return None
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        db = get_database()
        
        try:
            await db[self.collection_name].update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error updating last login: {str(e)}")
            return False
    
    def user_to_response(self, user: User) -> UserResponse:
        """Convert User model to UserResponse (safe data)"""
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            profile_picture=user.profile_picture,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )


# Singleton instance
user_service = UserService()