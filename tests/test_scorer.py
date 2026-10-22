from app.skills import extract_skills
from app.scorer import skill_score, split_jd
from app.parser import split_sections

RESUME = """Skills:
Python, SQL, Pandas, scikit-learn, FastAPI, Git
Projects:
Built a churn model with XGBoost and deployed with Docker."""

JD = """Required: Python, SQL, machine learning, Docker.
Nice to have: Spark, Tableau."""


def test_extract_aliases():
    assert {"python", "sql", "scikit-learn", "xgboost", "docker"} <= extract_skills(RESUME)


def test_cpp_boundary():
    assert "c++" in extract_skills("Worked with C++ and Python")
    assert "java" not in extract_skills("Worked with JavaScript")


def test_split_jd():
    req, pref = split_jd(JD)
    assert "Spark" not in req and "Spark" in pref


def test_skill_score():
    r = skill_score(RESUME, JD)
    assert "machine learning" in r["missing_required"]
    assert "spark" in r["missing_preferred"]
    assert 0 < r["score"] < 1


def test_sections():
    s = split_sections(RESUME)
    assert "Python" in s["skills"] and "churn" in s["projects"]
