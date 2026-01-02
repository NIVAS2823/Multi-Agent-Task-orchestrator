from typing import List, Optional, Literal
from typing_extensions import TypedDict


# =====================
# Event model
# =====================
class AgentEvent(TypedDict):
    agent: Literal["planner", "executor", "critic", "supervisor"]
    action: str
    detail: Optional[str]
    step_index: Optional[int]


# =====================
# FSM states
# =====================
class FSMState(TypedDict):
    fsm_state: Literal[
        "start",
        "plan",
        "execute",
        "critique",
        "advance",
        "complete",
        "fail",
    ]


# =====================
# Main Agent State
# =====================
class AgentState(TypedDict):
    # ---- Core request ----
    user_goal: str

    # ---- Planning ----
    plan: List[str]
    current_step: Optional[str]
    current_step_index: int

    # ---- Research (optional agent) ----
    # research_notes: List[str]

    # ---- Execution ----
    execution_history: List[str]           # ALL executor outputs
    execution_result: Optional[str]         # Current step output
    last_executor_output: Optional[str]     # 🔑 ALWAYS preserved

    # ---- Critique ----
    critique: Optional[str]
    is_approved: Optional[bool]

    # ---- FSM + Control ----
    fsm_state: Literal[
        "start",
        "plan",
        "execute",
        "critique",
        "advance",
        "complete",
        "fail",
    ]
    retry_count: int

    # ---- Routing ----
    next_agent: Optional[
        Literal["planner", "executor", "critic", "end"]
    ]

    # ---- Final Output ----
    final_output: Optional[str]

    # ---- Telemetry ----
    events: List[AgentEvent]
