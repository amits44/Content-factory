from langgraph.graph import StateGraph, END
from nodes import trend_researcher_node, script_writer_node, human_approval_node, publisher_node, voiceover_node
from langgraph.checkpoint.sqlite import SqliteSaver
from state import ContentState
from typing import Literal

def should_publish(state: ContentState) -> Literal["publisher", "script_writer", "trend_researcher"]:
    """Edge condition: approved → publish, rejected → rewrite"""
    if state["human_approved"]:
        return "publisher"
    if state.get("reject_topic"):
        return "trend_researcher"
    return "script_writer"

graph = StateGraph(ContentState)

graph.add_node("trend_researcher", trend_researcher_node)
graph.add_node("script_writer", script_writer_node)
graph.add_node("voiceover", voiceover_node)
graph.add_node("human_approval", human_approval_node)
graph.add_node("publisher", publisher_node)

graph.set_entry_point("trend_researcher")
graph.add_edge("trend_researcher", "script_writer")
graph.add_edge("trend_researcher", "script_writer")
graph.add_edge("script_writer", "voiceover")
graph.add_edge("voiceover", "human_approval")
graph.add_conditional_edges("human_approval", should_publish,{
        "publisher": "publisher",
        "script_writer": "script_writer",
        "trend_researcher": "trend_researcher"
    })
graph.add_edge("publisher", END)

with SqliteSaver.from_conn_string("content_factory.db") as memory:
    app = graph.compile(checkpointer=memory)

    config = {"configurable": {"thread_id": "run_004"}}
    
    print("Starting agent...")
    result = app.invoke({
        "niche": "fitness",
        "topic": "",
        "trend_reason": "",
        "script": "",
        "hook": "",
        "human_approved": False,
        "rejection_reason": "",
        "iteration_count": 0
    }, config=config)
    
    print("\nGraph paused! Current state:")
    print(result)