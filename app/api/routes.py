"""
Main API Routes

Handles execution of multi-agent tasks with authentication.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List

from app.graphs.builder import build_graph
from app.graphs.state import AgentState, AgentEvent
from app.services.session_service import session_service
from app.models.user import User  # NEW
from app.api.dependencies import get_current_user  # NEW
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

logger.info("🔧 Building agent graph...")
graph = build_graph()
logger.info("✅ Agent graph built successfully")


class RunRequest(BaseModel):
    user_goal: str = Field(
        ...,
        example="Best Indian city for 2026 vacation?",
        description="User task to be executed by the agent system",
    )


class RunResponse(BaseModel):
    final_output: str
    events: List[AgentEvent]
    session_id: str


@router.post("/run", response_model=RunResponse)
async def run_agent(
    request: RunRequest,
    current_user: User = Depends(get_current_user)  # NEW: Require authentication
):
    """
    Execute the multi-agent workflow (PROTECTED)
    
    Requires: Valid JWT token in Authorization header
    
    Behavior:
    - Creates a new session linked to the authenticated user
    - Executes multi-agent workflow
    - Saves conversation to user's session history
    """

    try:
        logger.info("=" * 80)
        logger.info(f"🎯 Task from user {current_user.username}: {request.user_goal[:100]}")
        logger.info("=" * 80)

        title = (
            request.user_goal[:50] + "..."
            if len(request.user_goal) > 50
            else request.user_goal
        )

        # Create session linked to user
        session_id = await session_service.create_session(
            title=title,
            user_id=str(current_user.id)  # NEW: Link to user
        )
        logger.info(f"📝 Created session for user {current_user.username}: {session_id}")

        user_saved = await session_service.add_message(
            session_id=session_id,
            role="user",
            content=request.user_goal,
        )

        if not user_saved:
            raise HTTPException(
                status_code=500,
                detail="Failed to save user message",
            )

        logger.info("💬 User message saved")

        initial_state: AgentState = {
            "user_goal": request.user_goal,
            "plan": [],
            "current_step": None,
            "current_step_index": 0,
            "research_notes": [],
            "execution_history": [],
            "execution_result": None,
            "critique": None,
            "is_approved": None,
            "next_agent": None,
            "final_output": None,
            "retry_count": 0,
            "events": [],
        }

        logger.info("🤖 Starting multi-agent execution...")
        logger.info("-" * 80)

        result = graph.invoke(initial_state)

        logger.info("-" * 80)
        logger.info("✅ Agent execution completed")

        final_output = result.get("final_output")
        events = result.get("events", [])

        if not final_output:
            raise HTTPException(
                status_code=500,
                detail="Agent execution produced no output",
            )

        assistant_saved = await session_service.add_message(
            session_id=session_id,
            role="assistant",
            content=final_output,
            metadata={
                "events": events,
                "plan": result.get("plan", []),
                "execution_history": result.get("execution_history", []),
            },
        )

        if not assistant_saved:
            raise HTTPException(
                status_code=500,
                detail="Failed to save assistant message",
            )

        logger.info("💬 Assistant response saved")

        logger.info("=" * 80)
        logger.info(f"🎉 Task completed for {current_user.username}")
        logger.info(f"📝 Session ID: {session_id}")
        logger.info(f"📊 Events: {len(events)}")
        logger.info("=" * 80)

        return RunResponse(
            final_output=final_output,
            events=events,
            session_id=session_id,
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ Agent execution failed: {str(e)}")
        logger.exception("Full traceback:")
        logger.error("=" * 80)

        raise HTTPException(
            status_code=500,
            detail="Agent execution failed",
        )