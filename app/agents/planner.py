from app.graphs.state import AgentState
from app.llm.factory import get_llm


def planner_node(state: AgentState) -> dict:
    llm = get_llm(temperature=0.7)
    
    prompt = f"""Create a step-by-step plan to accomplish this task:

TASK: {state['user_goal']}

Generate 2-4 clear, actionable steps. Each step should be specific and executable.
Return ONLY the steps as a Python list of strings, nothing else.

Example format:
['Step 1 description', 'Step 2 description', 'Step 3 description']"""

    response = llm.invoke(prompt)
    
    # Parse the plan
    import ast
    plan_str = response.content.strip()
    
    # Try to extract list from the response
    try:
        if '[' in plan_str:
            start = plan_str.index('[')
            end = plan_str.rindex(']') + 1
            plan = ast.literal_eval(plan_str[start:end])
        else:
            # Fallback: split by newlines
            plan = [line.strip() for line in plan_str.split('\n') if line.strip()]
    except:
        plan = [line.strip() for line in plan_str.split('\n') if line.strip()]
    
    print("\nPlan:")
    for i, step in enumerate(plan, 1):
        print(f"{i}. {step}")
    
    return {
        "plan": plan,
        "current_step": plan[0] if plan else None,
        "current_step_index": 0,
        "execution_history": [],  # Initialize empty history
        "retry_count": 0
    }