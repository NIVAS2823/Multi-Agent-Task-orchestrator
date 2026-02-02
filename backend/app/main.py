"""
Multi-Agent Task Orchestration System - Main Application

FastAPI application with MongoDB session management, logging, and authentication.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.api.routes import router
from app.api.session_routes import router as session_router
from app.api.auth_routes import router as auth_router  # NEW
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.utils.logger import setup_logging, get_logger

load_dotenv()

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
    
    try:
        await connect_to_mongo()
        logger.info("✅ All systems initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {str(e)}")
        raise
    
    yield
    
    logger.info("=" * 80)
    logger.info("🛑 Shutting down Multi-Agent Task Orchestration System")
    logger.info("=" * 80)
    
    try:
        await close_mongo_connection()
        logger.info("✅ System shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {str(e)}")
    
    logger.info("👋 Goodbye!")


app = FastAPI(
    title="Multi-Agent Task Orchestration System",
    description="LangGraph-powered Agentic AI backend with session management, logging, and authentication",
    version="3.0.0",  # Updated version
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


ALLOWED_ORIGINS = [
    "https://multi-agent-task-orchestrator.vercel.app",
    "http://localhost:5173",
    "https://multi-agent-task-orchestrator-ersn0ep5x.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    logger.info("📍 Root endpoint accessed")
    return {
        "message": "Multi-Agent Task Orchestration System",
        "version": "3.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "auth": "/api/auth"
    }


@app.get("/health")
async def health():
    """
    Health check endpoint - Public
    
    Returns system status and version information
    """
    logger.debug("🏥 Health check requested")
    return {
        "status": "ok",
        "version": "3.0.0",
        "message": "System is running normally"
    }


# Include API routers
app.include_router(auth_router, prefix="/api")      # NEW: Auth routes
app.include_router(router, prefix="/api")
app.include_router(session_router, prefix="/api")

# logger.info("📡 API routes registered:")
# logger.info("   - /api/auth/register (POST) - User registration")
# logger.info("   - /api/auth/login (POST) - User login")
# logger.info("   - /api/auth/me (GET) - Current user info")
# logger.info("   - /api/auth/google/login (GET) - Google OAuth")
# logger.info("   - /api/run (POST) - Execute task [PROTECTED]")
# logger.info("   - /api/sessions/ (GET, POST) - Manage sessions [PROTECTED]")
# logger.info("=" * 80)