"""
Main API Routes

Handles execution of multi-agent tasks.
Sessions are ALWAYS created server-side (GPT-style).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List

from app.graphs.builder import build_graph
from app.graphs.state import AgentState, AgentEvent
from app.services.session_service import session_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Build agent graph once at startup
logger.info("🔧 Building agent graph...")
graph = build_graph()
logger.info("✅ Agent graph built successfully")


# -------------------- REQUEST / RESPONSE MODELS --------------------

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


# -------------------- ROUTE --------------------

@router.post("/run", response_model=RunResponse)
async def run_agent(request: RunRequest):
    """
    Execute the multi-agent workflow.

    Behavior (GPT-style):
    - ALWAYS creates a new session
    - Client never supplies session_id
    - MongoDB owns ID generation
    """

    try:
        logger.info("=" * 80)
        logger.info(f"🎯 New task received: {request.user_goal[:100]}")
        logger.info("=" * 80)

        # -------------------- CREATE SESSION --------------------
        title = (
            request.user_goal[:50] + "..."
            if len(request.user_goal) > 50
            else request.user_goal
        )

        session_id = await session_service.create_session(title=title)
        logger.info(f"📝 Created new session: {session_id}")

        # -------------------- SAVE USER MESSAGE --------------------
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

        # -------------------- INITIAL AGENT STATE --------------------
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

        # -------------------- EXECUTE GRAPH --------------------
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

        # -------------------- SAVE ASSISTANT MESSAGE --------------------
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
        logger.info("🎉 Task completed successfully")
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
