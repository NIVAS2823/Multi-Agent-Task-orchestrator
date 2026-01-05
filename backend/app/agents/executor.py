from app.graphs.state import AgentState
from app.llm.factory import get_llm
from app.schemas.execution import ExecutionOutput
from pydantic import ValidationError


def executor_node(state: AgentState) -> dict:
    llm = get_llm(temperature=0.2)

    step = state.get("current_step")
    critique = state.get("critique")

    # ---------------- CONTEXT ----------------
    context = f"ORIGINAL TASK:\n{state['user_goal']}\n\n"

    if state.get("execution_history"):
        context += "\n=== PREVIOUS EXECUTIONS ===\n"
        for i, past in enumerate(state["execution_history"]):
            context += f"\nAttempt {i + 1}:\n{past}\n"
            context += "-" * 60 + "\n"

    context += f"\n=== CURRENT STEP ===\n{step}\n"

    if critique:
        context += f"\n=== CRITIC FEEDBACK (MUST FIX) ===\n{critique}\n"

    # ---------------- PROMPT ----------------
    prompt = f"""
You are an execution agent.

{context}

CRITICAL INSTRUCTIONS:
1. Fully COMPLETE the CURRENT STEP
2. Fix ALL issues mentioned in critic feedback
3. Do NOT ask questions or defer decisions
4. Do NOT repeat previous failed answers
5. Be clear, direct, and decisive

Return your answer in the following structured format:

- content: string
"""

    try:
        structured_llm = llm.with_structured_output(ExecutionOutput)
        result: ExecutionOutput = structured_llm.invoke(prompt)

    except ValidationError as e:
        # Schema failure → retryable, Supervisor will handle retries
        return {
            "execution_result": None,
            "schema_error": str(e),
            "fsm_state": "execute",
        }

    # ---------------- LOGGING ----------------
    print("\n" + "=" * 60)
    print(f"EXECUTOR - Step {state.get('current_step_index', 0) + 1}")
    print(result.content)
    print("=" * 60 + "\n")

    updated_history = state.get("execution_history", []).copy()
    updated_history.append(result.content)

    # ---------------- FSM RETURN ----------------
    return {
        # ---- Output ----
        "execution_result": result.content,
        "last_executor_output": result.content,
        "execution_history": updated_history,

        # ---- FSM ----
        "fsm_state": "critique",

        # ---- Cleanup ----
        "schema_error": None,
    }
