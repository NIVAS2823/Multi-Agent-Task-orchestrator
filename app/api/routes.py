from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from typing  import Optional

from app.graphs.builder import build_graph
from app.graphs.state import AgentState


router = APIRouter()
graph = build_graph()

class RunRequest(BaseModel):
    user_goal: str = Field(..., example="Explain India's cultural diversity in 50 words")


class RunResponse(BaseModel):
    final_output: str


@router.post("/run", response_model=RunResponse)
def run_agent(request: RunRequest):
    try:
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
        "retry_count": 0
        }

        result = graph.invoke(
            initial_state,
            config={
                "recursion_limit": 25
            }
        )

        return RunResponse(final_output=result["final_output"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
