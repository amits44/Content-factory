from typing import Literal
from app.state import ContentState
import os
from groq import Groq
from gtts import gTTS
import requests
import time
import json
from dotenv import load_dotenv
from app.prompts import get_trend_researcher_prompt
from app.pipeline_state import pipeline_paused_jobs, pipeline_decisions
load_dotenv()
client = Groq()

audio_outputs = "output/audio"
os.makedirs(audio_outputs, exist_ok=True)


def trend_researcher_node(state:ContentState)-> ContentState:
    """find one trending topic for the niche"""
    print(f"\n[Trend Researcher] finding topic for the niche: {state['niche']}")

    feedback = ""
    if state.get("topic_rejection_reason"):
        feedback = f"Previously rejected topic '{state.get('topic')}' because: {state['topic_rejection_reason']}. Find something different."

    try:
        response = requests.get(
            "https://serpapi.com/search",
            params={
                "engine": "google_trends_trending_now",
                "geo": "IN",
                "api_key": os.getenv("SERP_API_KEY")
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        trends = data.get("trending_searches", [])
        trend_titles = [t.get("query", "") for t in trends[:10]]
        print(f"[Trend Researcher] Got trends: {trend_titles}")

        formatted_prompt = get_trend_researcher_prompt(
            niche=state["niche"],
            filtered_titles= trend_titles,
            feedback=state.get("feedback", "")
        )

        response = client.chat.completions.create(
            model = "llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": formatted_prompt
            }],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        print(f"[Trend Researcher] Found: {result['topic']}")
        return{
            "topic": result["topic"],
            "trend_reason": result["reason"]
        }

    except requests.exceptions.Timeout:
        print("[Trend Researcher] SerpAPI timed out, using LLM fallback")
        return _llm_fallback_topic(state)

    except requests.exceptions.RequestException as e:
        print(f"[Trend Researcher] SerpAPI error: {e}, using LLM fallback")
        return _llm_fallback_topic(state)

def _llm_fallback_topic(state: ContentState) -> ContentState:
    """When SerpAPI fails, LLM picks a relevant trending topic from its knowledge"""

    feedback = ""
    if state.get("topic_rejection_reason"):
        feedback = f"Previously rejected topic '{state.get('topic')}' because: {state['topic_rejection_reason']}. Find something different."

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""Suggest ONE currently popular topic in {state['niche']} for short video content.
            {feedback}
            Respond in JSON only:
            {{"topic": "topic name", "reason": "why it's popular"}}"""
        }],
        response_format={"type": "json_object"}
    )
    result = json.loads(response.choices[0].message.content)
    return {
        "topic": result["topic"],
        "trend_reason": result["reason"] + " (LLM fallback)"
    }

def script_writer_node(state:ContentState)-> ContentState:
    """Write a video script for a  trending topic"""
    print(f"\n[Script Writer] writing script for topic: {state['topic']}")

    feedback = ""
    if state.get("rejection_reason"):
        feedback = f"Previous script was rejected because: {state['rejection_reason']}. Fix this."

    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""Write a 60-second short video script about: {state['topic']}
            Niche: {state['niche']}
            {feedback}
            Respond in JSON only:
            {{"hook": "opening line", "script": "full 60 second script"}}"""
        }],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    print(f"[Script Writer] Hook: {result['hook']}")
    return{
        "hook": result["hook"],
        "script": result["script"],
        "human_approved": False,
        "rejection_reason": ""
    }

def voiceover_node(state: ContentState) -> ContentState:
    print(f"\n[Voiceover] Generating audio for script...")
    try:
        tts= gTTS(text= state['script'], lang='en', slow=False) 
        file_name = f"audio_{state['topic'].replace(' ', '_')}.mp3"
        audio_path = os.path.join(audio_outputs, file_name)
        tts.save(audio_path)
        print(f"[Voiceover] Saved to {audio_path}")

        return {"audio_path": audio_path}
        
    except Exception as e:
        print(f"[Voiceover] Failed: {e}")
        return {"audio_path": ""}

def human_approval_node(state: ContentState) -> ContentState:
    """Pauses for human review"""
    print(f"\n[Human Approval] Reviewing script for topic: {state['topic']}")
    
    job_id = state.get("job_id","unknown")

    pipeline_paused_jobs[job_id]={
        "status": "waiting for approval",
        "topic": state["topic"],
        "hook": state["hook"],
        "script": state["script"]
    }
    while job_id not in pipeline_decisions:
        time.sleep(1)
    decision = pipeline_decisions.pop(job_id)
    pipeline_paused_jobs.pop(job_id, None) 

    if decision["action"] == "approve":
        return{
            "human_approved": True,
            "iteration_count": state["iteration_count"] + 1
        }
    elif decision["action"] == "reject":
        return {
            "human_approved": False,
            "reject_topic": True,
            "topic_rejection_reason": decision["reason"]
        }
    else:
        return {
            "human_approved": False,
            "rejection_reason": decision["reason"],
            "iteration_count": state["iteration_count"] + 1
        }

def publisher_node(state: ContentState) -> ContentState:
    """Publishes the approved content"""
    print(f"\n[Publisher] Publishing: {state['topic']}")
    print(f"Hook: {state['hook']}")
    print("[Publisher] Successfully published! (mock)")
    return state