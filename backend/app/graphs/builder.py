from langgraph.graph import StateGraph,END,START
from app.graphs.state import AgentState
from app.agents.critic import critic_node
from app.agents.supervisor import supervisor_node
from app.agents.planner import planner_node
from app.agents.executor import executor_node
# from app.agents.researcher import researcher_node


def build_graph():
    graph = StateGraph(AgentState)


    graph.add_node("supervisor",supervisor_node)
    graph.add_node("planner",planner_node)
    # graph.add_node("researcher",researcher_node)
    graph.add_node("executor",executor_node)
    graph.add_node("critic",critic_node)


    graph.set_entry_point("supervisor")

    graph.add_edge("planner","supervisor")
    # graph.add_edge("researcher","supervisor")
    graph.add_edge("executor","supervisor")
    graph.add_edge("critic","supervisor")

    def route(state:AgentState):
        return state["next_agent"]
    
    graph.add_conditional_edges(
        "supervisor",
        route,
        {
            "planner":"planner",
            # "researcher":"researcher",
            "executor":"executor",
            "critic":"critic",
            "supervisor": "supervisor",
            "end":END
        },
    )


    return graph.compile()