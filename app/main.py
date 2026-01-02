"""
Multi-Agent Task Orchestration System - Main Application

FastAPI application with MongoDB session management and logging.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.api.routes import router
from app.api.session_routes import router as session_router
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.utils.logger import setup_logging, get_logger

# Load environment variables from .env file
load_dotenv()

# Setup logging system
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    
    Handles startup and shutdown events:
    - Startup: Initialize MongoDB connection and logging
    - Shutdown: Close MongoDB connection gracefully
    """
    # # ===== STARTUP =====
    # logger.info("=" * 80)
    # logger.info("🚀 Starting Multi-Agent Task Orchestration System")
    # logger.info("=" * 80)
    
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        logger.info("✅ All systems initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {str(e)}")
        raise
    
    yield
    
    # ===== SHUTDOWN =====
    logger.info("=" * 80)
    logger.info("🛑 Shutting down Multi-Agent Task Orchestration System")
    logger.info("=" * 80)
    
    try:
        # Close MongoDB connection
        await close_mongo_connection()
        logger.info("✅ System shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {str(e)}")
    
    logger.info("👋 Goodbye!")


# Create FastAPI application
app = FastAPI(
    title="Multi-Agent Task Orchestration System",
    description="LangGraph-powered Agentic AI backend with session management and logging",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Update this in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    logger.info("📍 Root endpoint accessed")
    return {
        "message": "Multi-Agent Task Orchestration System",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """
    Health check endpoint
    
    Returns system status and version information
    """
    logger.debug("🏥 Health check requested")
    return {
        "status": "ok",
        "version": "2.0.0",
        "message": "System is running normally"
    }


# Include API routers
app.include_router(router, prefix="/api")
app.include_router(session_router, prefix="/api")

# logger.info("📡 API routes registered:")
# logger.info("   - /api/run (POST) - Execute multi-agent task")
# logger.info("   - /api/sessions/ (GET, POST) - Manage sessions")
# logger.info("   - /api/sessions/{id} (GET, PATCH, DELETE) - Session operations")
# logger.info("=" * 80)