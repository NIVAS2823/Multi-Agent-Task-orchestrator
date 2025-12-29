from app.llm.factory import get_llm
from app.tools.search import search_tool
from app.graphs.state import AgentState

def researcher_node(state:AgentState)->dict:
    llm = get_llm(temperature=0.2)
    query = state['current_step']

    raw_results = search_tool(query)

    prompt = (
        "You are a research agent.\n"
        "Summarize the following information concisely.\n"
        "Focus only on facts relevant to the task.\n\n"
        f"DATA:\n{raw_results}"
    )

    summary = llm.invoke(prompt)

    print("\nSummary from research:",end='')
    print(f"{summary.content}")
    return {
        "research_notes":state["research_notes"] + [summary.content]
    }

