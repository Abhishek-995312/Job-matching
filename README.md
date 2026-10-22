# AI Resume Analyzer and Job Matching System

Scores a resume against a job description using skill matching and semantic similarity.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                                  # unit tests
uvicorn app.main:app --reload           # open http://127.0.0.1:8000/docs
```

## Structure
- `app/parser.py` - PDF/DOCX text extraction, cleaning, section splitting
- `app/skills.py` - skill extraction with alias normalisation (`data/skills.json`)
- `app/scorer.py` - skill score, semantic score, final weighted score
- `app/main.py` - FastAPI endpoint `POST /analyze`
- `tests/` - unit tests

## Roadmap
1. Parsing and extraction on 10+ real resumes
2. Tune weights using labeled resume-JD pairs
3. Frontend, LLM suggestions, job ranking, deployment
