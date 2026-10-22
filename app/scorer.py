"""Step 3: skill-overlap score + semantic similarity + final weighted score."""
import re
from functools import lru_cache

from .skills import extract_skills

PREFERRED_MARKER = re.compile(
    r"(preferred|nice to have|good to have|bonus|plus point)", re.IGNORECASE
)

WEIGHTS = {"skill": 0.6, "semantic": 0.4}  # tune these using your labeled pairs


def split_jd(jd_text: str):
    """Text after a 'preferred / nice to have' marker counts as optional."""
    m = PREFERRED_MARKER.search(jd_text)
    if not m:
        return jd_text, ""
    return jd_text[: m.start()], jd_text[m.start():]


def skill_score(resume_text: str, jd_text: str) -> dict:
    required_part, preferred_part = split_jd(jd_text)
    resume_skills = extract_skills(resume_text)
    required = extract_skills(required_part)
    preferred = extract_skills(preferred_part) - required

    # required skills weigh 1.0, preferred skills 0.5
    total = len(required) * 1.0 + len(preferred) * 0.5
    matched_req = required & resume_skills
    matched_pref = preferred & resume_skills
    got = len(matched_req) * 1.0 + len(matched_pref) * 0.5
    score = got / total if total else 0.0

    return {
        "score": round(score, 3),
        "matched": sorted(matched_req | matched_pref),
        "missing_required": sorted(required - resume_skills),
        "missing_preferred": sorted(preferred - resume_skills),
    }


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def semantic_score(resume_text: str, jd_text: str) -> float:
    from sentence_transformers import util
    emb = _model().encode([resume_text, jd_text], convert_to_tensor=True)
    sim = float(util.cos_sim(emb[0], emb[1]))
    return round(max(0.0, min(1.0, sim)), 3)


def final_score(resume_text: str, jd_text: str) -> dict:
    s = skill_score(resume_text, jd_text)
    sem = semantic_score(resume_text, jd_text)
    total = WEIGHTS["skill"] * s["score"] + WEIGHTS["semantic"] * sem
    return {
        "compatibility_percent": round(total * 100, 1),
        "skill_score": s["score"],
        "semantic_score": sem,
        "matched_skills": s["matched"],
        "missing_required": s["missing_required"],
        "missing_preferred": s["missing_preferred"],
    }
