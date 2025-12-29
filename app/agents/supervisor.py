from app.graphs.state import AgentState


def supervisor_node(state: AgentState) -> dict:
    plan = state.get("plan") or []
    is_approved = state.get("is_approved")
    execution_result = state.get("execution_result")
    critique = state.get("critique")
    retry_count = state.get("retry_count", 0)
    current_step_index = state.get("current_step_index", 0)

    print(f"\n[SUPERVISOR] Current step: {current_step_index + 1}/{len(plan)}, Retry: {retry_count}")

   
    if retry_count >= 3:  # Increased to 3 for more attempts
        final = "\n\n".join(state.get("execution_history", []))
        return {
            "next_agent": "end",
            "final_output": f"Task stopped after repeated failed executions.\n\nPartial results:\n{final}"
        }

    # 1️⃣ INITIAL — no plan yet
    if not plan:
        return {"next_agent": "planner"}

    # 2️⃣ EXECUTION REQUIRED — no result yet
    if execution_result is None:
        return {"next_agent": "executor"}

    # 3️⃣ CRITIQUE REQUIRED — execution exists but not reviewed
    if critique is None:
        return {"next_agent": "critic"}

    # 4️⃣ STEP APPROVED — advance to next step
    if is_approved is True:
        next_index = current_step_index + 1
        
        # Check if all steps complete
        if next_index >= len(plan):
            final = "\n\n".join(state.get("execution_history", []))
            return {
                "next_agent": "end",
                "final_output": final
            }
        
        # Move to next step
        return {
            "current_step": plan[next_index],
            "current_step_index": next_index,
            "execution_result": None,
            "critique": None,
            "is_approved": None,
            "retry_count": 0,  # Reset on success
            "next_agent": "executor",
        }

    # 5️⃣ STEP FAILED — retry executor (bounded)
    if is_approved is False:
        print(f"--- RETRY {retry_count + 1}: {critique} ---")
        return {
            "execution_result": None,
            "critique": None,
            "is_approved": None,
            "retry_count": retry_count + 1,
            "next_agent": "executor",
        }

    # 6️⃣ SAFETY NET
    return {"next_agent": "end"}