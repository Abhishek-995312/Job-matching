"""Step 4: LLM-powered suggestions (resume rewrites, skill-gap advice, interview questions).

Works without an API key: falls back to simple rule-based suggestions.
Set ANTHROPIC_API_KEY (and optionally LLM_MODEL) to enable the LLM.
"""
import json
import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq

MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
MAX_CHARS = 6000  # keep prompts small and cheap

SYSTEM_PROMPT = """You are a careful resume coach for students and freshers.

Rules:
- Use ONLY facts that appear in the resume. Never invent employers, projects, skills, numbers or achievements.
- If an improved bullet needs a metric the resume doesn't give, use a placeholder like [X%] or [N users] for the candidate to fill in.
- For missing skills, explain how the candidate can learn or demonstrate the skill (a small project, a course). Never suggest claiming a skill they don't have.
- Keep advice specific to this resume and job description.
- Return ONLY valid JSON, no markdown fences, matching this schema:
{
  "summary": "2-3 sentence overall assessment",
  "bullet_rewrites": [{"original": "...", "improved": "...", "why": "..."}],
  "skill_gap_advice": [{"skill": "...", "how_to_address": "..."}],
  "interview_questions": [{"question": "...", "type": "technical|project|behavioral"}]
}
Give 3 bullet_rewrites, up to 5 skill_gap_advice items, and 6 interview_questions."""


def build_user_prompt(resume_text: str, jd_text: str, analysis: dict) -> str:
    return (
        f"RESUME:\n{resume_text[:MAX_CHARS]}\n\n"
        f"JOB DESCRIPTION:\n{jd_text[:MAX_CHARS]}\n\n"
        f"AUTOMATED ANALYSIS:\n"
        f"- compatibility: {analysis.get('compatibility_percent')}%\n"
        f"- matched skills: {analysis.get('matched_skills')}\n"
        f"- missing required skills: {analysis.get('missing_required')}\n"
        f"- missing preferred skills: {analysis.get('missing_preferred')}\n"
    )


def parse_json(text: str) -> dict:
    """Tolerate code fences or stray text around the JSON object."""
    text = text.strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model output")
    return json.loads(text[start : end + 1])


def fallback_suggestions(analysis: dict) -> dict:
    advice = [
        {
            "skill": s,
            "how_to_address": f"Build a small project that uses {s} and add it "
                              f"to your Projects section with a measurable result.",
        }
        for s in analysis.get("missing_required", [])[:5]
    ]
    return {
        "summary": (
            f"Compatibility is {analysis.get('compatibility_percent')}%. "
            "Focus on the missing required skills and add measurable results to your bullets."
        ),
        "bullet_rewrites": [],
        "skill_gap_advice": advice,
        "interview_questions": [],
        "source": "rule-based",
    }


def get_suggestions(resume_text: str, jd_text: str, analysis: dict) -> dict:
    if not os.getenv("GROQ_API_KEY"):
        return fallback_suggestions(analysis)

    client = Groq()  # reads GROQ_API_KEY automatically
    resp = client.chat.completions.create(
        model=MODEL,
        max_tokens=1500,
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(resume_text, jd_text, analysis)},
        ],
    )
    text = resp.choices[0].message.content
    data = parse_json(text)
    data["source"] = "llm"
    return data
