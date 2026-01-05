from app.graphs.state import AgentState
from app.llm.factory import get_llm
from pydantic import BaseModel, Field


class CriticOutput(BaseModel):
    approved: bool = Field(
        description="Whether the current step was completed correctly"
    )
    feedback: str = Field(
        description="Brief explanation of the decision"
    )


def critic_node(state: AgentState) -> dict:
    llm = get_llm(temperature=0)

    result_text = state.get("execution_result", "")
    current_step = state.get("current_step", "")

    # -------------------- DETERMINISTIC GUARDS --------------------
    if not result_text or not result_text.strip():
        return {
            "critique": "Executor produced no output for this step.",
            "is_approved": False,
        }

    # -------------------- OPTIONAL CONTEXT --------------------
    context = ""
    if state.get("execution_history"):
        completed_steps = max(len(state["execution_history"]) - 1, 0)
        context = f"Previous steps completed successfully: {completed_steps}\n"

    # -------------------- PROMPT --------------------
    prompt = f"""
You are a quality control agent (critic).

{context}

CURRENT STEP REQUIREMENT:
{current_step}

EXECUTION RESULT TO EVALUATE:
{result_text}

EVALUATION RULES (VERY IMPORTANT):
1. APPROVE only if the executor clearly COMPLETED the step.
2. REJECT if the executor:
   - Avoided making a decision
   - Gave generic advice instead of an answer
   - Asked questions instead of completing the task
   - Ignored explicit requirements in the step
3. Do NOT judge based on length, formatting, or style.
4. Be practical, not perfectionist.
5. Executor is allowed to use general knowledge when completing steps.

Respond with:
- approved: true or false
- feedback: one short sentence explaining why
"""

    critique = llm.with_structured_output(CriticOutput).invoke(prompt)

    # -------------------- LOGGING --------------------
    print("\n" + "=" * 60)
    print("CRITIC EVALUATION")
    print("=" * 60)
    print(f"Approved: {critique.approved}")
    print(f"Feedback: {critique.feedback}")
    print("=" * 60 + "\n")

    return {
        "critique": critique.feedback,
        "is_approved": critique.approved,
    }
