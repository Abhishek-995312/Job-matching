import pytest
from app.llm import parse_json, fallback_suggestions, get_suggestions, build_user_prompt

ANALYSIS = {
    "compatibility_percent": 61.5,
    "matched_skills": ["python", "sql"],
    "missing_required": ["docker", "machine learning"],
    "missing_preferred": ["spark"],
}


def test_parse_json_plain_and_fenced():
    assert parse_json('{"a": 1}') == {"a": 1}
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json('Here you go: {"a": {"b": 2}} done') == {"a": {"b": 2}}


def test_parse_json_rejects_garbage():
    with pytest.raises(ValueError):
        parse_json("no json here")


def test_fallback_uses_missing_skills():
    out = fallback_suggestions(ANALYSIS)
    assert [a["skill"] for a in out["skill_gap_advice"]] == ["docker", "machine learning"]
    assert out["source"] == "rule-based"


def test_no_api_key_uses_fallback(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert get_suggestions("resume", "jd", ANALYSIS)["source"] == "rule-based"


def test_prompt_contains_analysis():
    p = build_user_prompt("my resume", "my jd", ANALYSIS)
    assert "docker" in p and "61.5" in p
