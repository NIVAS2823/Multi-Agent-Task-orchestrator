from app.graphs.state import AgentState
from app.llm.factory import get_llm
from pydantic import BaseModel, Field


class CriticOutput(BaseModel):
    approved: bool = Field(description="Whether the current step was completed correctly")
    feedback: str = Field(description="Brief explanation of the decision")


def critic_node(state: AgentState) -> dict:
    llm = get_llm(temperature=0)

    # Show critic the context too
    context = ""
    if state.get("execution_history"):
        context = f"Previous steps completed: {len(state['execution_history']) - 1}\n"

    # Count words in execution result
    result_text = state['execution_result']
    word_count = len(result_text.split())

    prompt = f"""You are a quality control agent.

{context}
CURRENT STEP REQUIREMENT: {state['current_step']}

EXECUTION RESULT TO EVALUATE:
{result_text}

WORD COUNT: {word_count} words

EVALUATION CRITERIA:
1. Did the executor actually COMPLETE the step (not just ask for information)?
2. If the step mentions a word limit (e.g., "50 words"), check if the result is reasonably close:
   - For 50 words: Accept 40-60 words (±20% is reasonable)
   - For 100 words: Accept 80-120 words
   - Slightly over/under is ACCEPTABLE - be lenient
3. Does the result make sense and provide useful information?

IMPORTANT: 
- If the executor says "please provide context" or asks questions, mark as NOT APPROVED
- For word limits, be LENIENT - a few words over is perfectly fine
- Focus on whether the task is COMPLETE, not perfectionism

Provide your evaluation:"""

    critique = llm.with_structured_output(CriticOutput).invoke(prompt)

    print(f"\n{'='*60}")
    print(f"CRITIC EVALUATION")
    print(f"{'='*60}")
    print(f"Word Count: {word_count}")
    print(f"Approved: {critique.approved}")
    print(f"Feedback: {critique.feedback}")
    print(f"{'='*60}\n")

    return {
        "critique": critique.feedback,
        "is_approved": critique.approved,
    }