from app.graphs.state import AgentState
from app.llm.factory import get_llm


def executor_node(state: AgentState) -> dict:
    llm = get_llm(temperature=0.2)

    step = state["current_step"]
    critique = state.get("critique")

    # BUILD FULL CONTEXT
    context = f"ORIGINAL TASK:\n{state['user_goal']}\n\n"

    if state.get("execution_history"):
        context += "=== PREVIOUS EXECUTIONS ===\n"
        for i, past in enumerate(state["execution_history"]):
            context += f"\nAttempt {i + 1}:\n{past}\n"
            context += "-" * 60 + "\n"

    context += f"\n=== CURRENT STEP ===\n{step}\n"

    if critique:
        context += f"\n=== CRITIC FEEDBACK (MUST FIX) ===\n{critique}\n"

    word_limit_instruction = ""
    if "50" in step:
        word_limit_instruction = (
            "\n⚠️ WORD COUNT RULE:\n"
            "Your response MUST be between 45 and 55 words.\n"
            "Responses outside this range are INVALID.\n"
        )

    prompt = f"""
You are an execution agent.

{context}

CRITICAL INSTRUCTIONS:
1. Use previous executions as context
2. Fix ALL issues mentioned in critic feedback
3. Fully complete the CURRENT STEP
4. Do NOT repeat previous failed answers
5. Be concise but complete
{word_limit_instruction}

Now produce the corrected execution result:
"""

    result = llm.invoke(prompt)
    word_count = len(result.content.split())

    print("\n" + "=" * 60)
    print(f"EXECUTOR - Step {state.get('current_step_index', 0) + 1}")
    print(f"Word Count: {word_count}")
    print("=" * 60)
    print(result.content)
    print("=" * 60 + "\n")

    updated_history = state.get("execution_history", []).copy()
    updated_history.append(result.content)

    return {
        "execution_result": result.content,
        "execution_history": updated_history,
    }
