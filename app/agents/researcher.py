from app.llm.factory import get_llm
from app.tools.search import search_tool
from app.graphs.state import AgentState


def researcher_node(state: AgentState) -> dict:
    llm = get_llm(temperature=0.2)

    query = state["current_step"]

    raw_results = search_tool(query)

    prompt = (
        "You are a research agent.\n"
        "Summarize the following information concisely.\n"
        "Focus only on facts relevant to the task.\n"
        "Do NOT add opinions or recommendations.\n\n"
        f"DATA:\n{raw_results}"
    )

    if not raw_results or not str(raw_results).strip():
        summary_text = "No relevant research results were found."
    else:
        summary = llm.invoke(prompt)
        summary_text = summary.content

    print("\n" + "=" * 60)
    print("RESEARCH SUMMARY")
    print("=" * 60)
    print(summary_text)
    print("=" * 60 + "\n")

    updated_notes = state.get("research_notes", []).copy()
    updated_notes.append(summary_text)

    return {
        "research_notes": updated_notes,
        "fsm_state": "execute",
    }
