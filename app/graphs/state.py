from typing import TypedDict, List, Optional, Literal, Dict

class AgentState(TypedDict):
    user_goal: str
    
    plan: List[str]
    current_step: Optional[str]
    current_step_index: int  # Track which step we're on
    
    research_notes: List[str]
    execution_history: List[str]  # Stores ALL past execution results
    execution_result: Optional[str]  # Current step result
    
    critique: Optional[str]
    is_approved: Optional[bool]  # Changed to bool for clarity
    
    next_agent: Optional[
        Literal["planner", "researcher", "executor", "critic", "end"]
    ]
    
    final_output: Optional[str]
    retry_count: int