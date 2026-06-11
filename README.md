# Trend to Video

A multi-agent pipeline that finds trending topics, writes a short video script, generates voiceover audio, and waits for human approval before publishing — all triggered via API.

## How it works

1. Fetches trending topics from Google Trends (SerpAPI)
2. LLM filters for niche relevance and picks one topic
3. Writes a 60-second video script
4. Generates voiceover audio (gTTS)
5. Pauses — waits for human approval via API
6. On approval, publishes. On rejection, rewrites with feedback.

## API

```
POST /generate          start a pipeline run
GET  /status/{job_id}   check status or get pending script for review
POST /approve/{job_id}  approve, reject script, or reject topic
```

Approval actions:
```json
{ "action": "approve", "reason": "" }
{ "action": "reject_script", "reason": "hook is too generic" }
{ "action": "reject_topic", "reason": "not relevant to niche" }
```

## Stack

LangGraph · FastAPI · Groq (llama-3.3-70b) · SerpAPI · gTTS · SQLite checkpointing · Render

## Run locally

```bash
cd Backend
source venv/bin/activate
cp .env.example .env  # add GROQ_API_KEY and SERP_API_KEY
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API.

## Live API

`https://your-render-url.onrender.com/docs`