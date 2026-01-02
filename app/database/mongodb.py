"""
MongoDB Database Connection Module

This module handles the connection to MongoDB using Motor (async driver).
It provides functions to connect, disconnect, and get the database instance.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MongoDB:
    """MongoDB connection singleton"""
    client: AsyncIOMotorClient = None
    db = None


# Global instance
mongodb = MongoDB()


async def connect_to_mongo():
    """
    Connect to MongoDB database
    
    Reads connection details from environment variables:
    - MONGODB_URL: MongoDB connection string (default: mongodb://localhost:27017)
    - MONGODB_DB_NAME: Database name (default: multi_agent_system)
    
    Raises:
        ConnectionFailure: If connection to MongoDB fails
    """
    try:
        # Get MongoDB URL from environment
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        
        # Create async motor client
        mongodb.client = AsyncIOMotorClient(mongodb_url)
        
        # Test the connection
        await mongodb.client.admin.command('ping')
        
        # Get database name from environment
        db_name = os.getenv("MONGODB_DB_NAME", "multi_agent_system")
        mongodb.db = mongodb.client[db_name]
        
        logger.info(f"✅ Successfully connected to MongoDB database: {db_name}")
        logger.info(f"📡 MongoDB URL: {mongodb_url}")
        
    except ConnectionFailure as e:
        logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
        logger.error("💡 Make sure MongoDB is running and connection details are correct")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error connecting to MongoDB: {str(e)}")
        raise


async def close_mongo_connection():
    """
    Close MongoDB connection gracefully
    
    Should be called during application shutdown
    """
    if mongodb.client:
        mongodb.client.close()
        logger.info("🔌 MongoDB connection closed successfully")
    else:
        logger.warning("⚠️ No MongoDB connection to close")


def get_database():
    """
    Get the MongoDB database instance
    
    Returns:
        Database: MongoDB database instance
        
    Raises:
        RuntimeError: If database connection hasn't been established
    """
    if mongodb.db is None:
        error_msg = "Database not initialized. Call connect_to_mongo() first."
        logger.error(f"❌ {error_msg}")
        raise RuntimeError(error_msg)
    
    return mongodb.db