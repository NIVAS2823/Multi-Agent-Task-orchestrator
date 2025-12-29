from fastapi import FastAPI
from app.api.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Multi-Agent Task Orchestration System",
    description="LangGraph-powered Agentic AI backend",
    version="1.0.0",
)

app.include_router(router, prefix="/api")
