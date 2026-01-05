from app.graphs.state import AgentState
from app.llm.factory import get_llm
import ast


def planner_node(state: AgentState) -> dict:
    llm = get_llm(temperature=0.7)

    prompt = f"""
Create a clear, step-by-step plan to accomplish the following task.

TASK:
{state['user_goal']}

RULES:
- Generate 2 to 4 steps only
- Each step must start with an action verb (e.g., Research, Compare, Decide, Produce)
- Steps must be concrete and executable
- Do NOT include explanations
- Return ONLY a Python list of strings

Example:
['Research top cities', 'Compare options', 'Choose best city']
"""

    response = llm.invoke(prompt)
    plan_str = response.content.strip()

    # -------------------- PARSE PLAN --------------------
    try:
        if "[" in plan_str:
            start = plan_str.index("[")
            end = plan_str.rindex("]") + 1
            plan = ast.literal_eval(plan_str[start:end])
        else:
            plan = [line.strip() for line in plan_str.split("\n") if line.strip()]
    except Exception:
        plan = [line.strip() for line in plan_str.split("\n") if line.strip()]

    # -------------------- SAFETY GUARDS --------------------
    plan = [str(step).strip() for step in plan if str(step).strip()]
    plan = plan[:4]  # hard cap: max 4 steps

    if not plan:
        plan = ["Produce a final, complete answer to the task"]

    # -------------------- LOG --------------------
    print("\nPLAN GENERATED:")
    for i, step in enumerate(plan, 1):
        print(f"{i}. {step}")

    # -------------------- RETURN STATE --------------------
    return {
        # ---- Planning ----
        "plan": plan,
        "current_step": plan[0],
        "current_step_index": 0,

        # ---- FSM CONTROL (Supervisor owns routing) ----
        "fsm_state": "execute",

        # ---- Reset execution state ----
        "execution_history": [],
        "execution_result": None,
        "last_executor_output": None,
        "critique": None,
        "is_approved": None,
        "retry_count": 0,
    }
