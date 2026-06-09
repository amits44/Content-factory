from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid
import json
from graph import run_pipeline

app = FastAPI(title="Content Factory API")

jobs = {}

class PipelineRequest(BaseModel):
    niche:str

class JobStatus(BaseModel):
    job_id: str
    status: str
    result: dict |None=None

@app.post("/generate", response_model=JobStatus)
async def generate_content(request: PipelineRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id]= {"status": "pending", "result": None}

    background_tasks.add_task(run_job, job_id, request.niche)
    return JobStatus(job_id = job_id, status="pending")

def run_job(job_id: str, niche: str):
    try:
        jobs[job_id]["status"]= "running"
        result = run_pipeline(niche=niche, thread_id = job_id)
        jobs[job_id]["status"]= "completed"
        jobs[job_id]["result"]= result
    except Exception as e:
        jobs[job_id]["status"]= "failed"
        jobs[job_id]["result"]= {"error": str(e)}

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id:str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    return JobStatus(job_id=job_id, status=job["status"], result=job["result"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}