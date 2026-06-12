import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.pipeline_state import pipeline_paused_jobs

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code ==200
    assert response.json() == {"status":"ok"}

def test_generate_job_id():
    with patch("app.main.run_job") as mock_bg:
        response = client.post("/generate", json={"niche": "fitness"})
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"

def test_status_unknown_job():
    response = client.get("/status/nonexistent-job-id")
    assert response.status_code == 404

def test_approve_non_pending_job():
    response = client.post("/approve/nonexistent-job-id",json={"action": "approve", "reason": ""})
    assert response.status_code ==400

def test_approve_actions():
    job_id = "test-pending-job"
    pipeline_paused_jobs[job_id] = {
        "topic": "HIIT",
        "hook": "test hook",
        "script": "test script",
        "audio_path": ""
    }
    for action in ["approve", "reject_script", "reject_topic"]:
        pipeline_paused_jobs[job_id] = {"topic": "HIIT", "hook": "h", "script": "s", "audio_path": ""}
        response = client.post(
            f"/approve/{job_id}",
            json={"action": action, "reason": "test reason"}
        )
        assert response.status_code == 200
        assert response.json()["job_id"] == job_id