import pytest
import requests as req
from unittest.mock import patch, MagicMock
from app.nodes import trend_researcher_node, script_writer_node
from app.state import ContentState

def base_state(**overrides)-> ContentState:
    state={
        "job_id": "test1",
        "niche": "fitness",
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
    }
    state.update(overrides)
    return state

class TestTrendResearcher:

    @patch("app.nodes.requests.get")
    @patch("app.nodes.client.chat.completions.create")
    def test_returns_clean_topic(self,mock_groq,mock_requests):
        mock_requests.return_value.json.return_value={
            "trending_searches":[
                {"query":"home workouts"},
                {"query":"HIIT workouts"}
            ]
        }
        mock_requests.return_value.raise_for_status = MagicMock()

        mock_groq.return_value.choices[0].message.content= (
            '{"topic": "home workouts", "reason": "high search volume", "source": "trending_list"}'
        )
        result = trend_researcher_node(base_state())

        assert "topic" in result
        assert result["topic"] == "home workouts"
        assert "none from" not in result["topic"].lower()
        assert "suggesting" not in result["topic"].lower()

    @patch("app.nodes.requests.get")
    @patch("app.nodes.client.chat.completions.create")
    def test_fallsback_to_llm_response_on_serp_timeout(self, mock_groq, mock_requests):
        mock_requests.side_effect = req.exceptions.Timeout()

        mock_groq.return_value.choices[0].message.content=(
            '{"topic": "yoga for beginner", "reason": "popular fitness topic"}'
        )
        result = trend_researcher_node(base_state())
        assert "topic" in result
        assert result["topic"]== "yoga for beginner"
        assert "LLM fallback" in result["trend_reason"]

    @patch("app.nodes.requests.get")
    @patch("app.nodes.client.chat.completions.create")
    def test_uses_rejection_feedback(self, mock_groq, mock_requests):
        mock_requests.return_value.json.return_value= {"trending_searches": []}
        mock_requests.return_value.raise_for_status = MagicMock()

        mock_groq.return_value.choices[0].message.content = (
            '{"topic": "strength training", "reason": "different from rejected topic", "source": "llm_knowledge"}'
        )
        state = base_state(
            topic = "french open",
            topic_rejection_reason="french open is a sports topic not fitness"
        )
        result = trend_researcher_node(state)

        call_args= mock_groq.call_args
        prompt_content = call_args[1]["messages"][0]["content"]
        assert "french open" in prompt_content.lower()
        assert result["topic"] == "strength training"


class TestScriptWriter:
    @patch("app.nodes.client.chat.completions.create")
    def test_return_hook_and_scripts(self, mock_groq):
        mock_groq.return_value.choices[0].message.content= (
            '{"hook": "Get ready to transform your body", "script": "Full 60 second script here..."}'
        )
        result = script_writer_node(base_state(topic="HIIT workout", niche="fitness"))

        assert result["hook"] == "Get ready to transform your body"
        assert result["script"] == "Full 60 second script here..."
        assert result["human_approved"] == False
        assert result["rejection_reason"] == ""

    @patch("app.nodes.client.chat.completions.create")
    def test_includes_rejection_feedback_in_prompt(self, mock_groq):
        mock_groq.return_value.choices[0].message.content = (
            '{"hook": "Better hook", "script": "Improved script"}'
        )

        state = base_state(
            topic="HIIT workout",
            rejection_reason="hook uses jargon most people don't understand"
        )
        script_writer_node(state)

        call_args = mock_groq.call_args
        prompt = call_args[1]["messages"][0]["content"]
        assert "hook uses jargon" in prompt