from langgraph.graph import StateGraph, END
from app.nodes import (trend_researcher_node, script_writer_node,video_generator_node,
                     human_approval_node, publisher_node, voiceover_node,)
from langgraph.checkpoint.sqlite import SqliteSaver
from app.state import ContentState
from typing import Literal
import sqlite3

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
graph.add_node("video_generator", video_generator_node)
graph.add_node("human_approval", human_approval_node)
graph.add_node("publisher", publisher_node)

graph.set_entry_point("trend_researcher")
graph.add_edge("trend_researcher", "script_writer")
graph.add_edge("trend_researcher", "script_writer")
graph.add_edge("script_writer", "voiceover")
graph.add_edge("voiceover", "video_generator")
graph.add_edge("video_generator", "human_approval")
graph.add_conditional_edges("human_approval", should_publish,{
        "publisher": "publisher",
        "script_writer": "script_writer",
        "trend_researcher": "trend_researcher"
    })
graph.add_edge("publisher", END)

conn = sqlite3.connect("content_factory.db", check_same_thread=False)
memory = SqliteSaver(conn)
app= graph.compile(checkpointer=memory)

def run_pipeline(niche: str, thread_id: str)-> dict:

    config = {"configurable": {"thread_id": thread_id}}

    result = app.invoke({
        "job_id": thread_id,
        "niche": niche,
        "topic": "",
        "trend_reason": "",
        "reject_topic": False,
        "topic_rejection_reason": "",
        "script": "",
        "hook": "",
        "audio_path": "",
        "human_approved": False,
        "rejection_reason": "",
        "iteration_count": 0
    }, config=config)
    
    return result