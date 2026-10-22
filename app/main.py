from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from .llm import get_suggestions
from .parser import extract_text_from_bytes, split_sections
from .scorer import final_score

app = FastAPI(title="AI Resume Analyzer and Job Matching System")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(
        resume: UploadFile = File(...),
        jd_text: str = Form(...),
        include_suggestions: bool = Form(True),
):
    data = await resume.read()
    try:
        text = extract_text_from_bytes(data, resume.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if len(text) < 50:
        raise HTTPException(status_code=422, detail="Could not read text from resume")

    result = await run_in_threadpool(final_score, text, jd_text)
    result["sections_found"] = [k for k, v in split_sections(text).items() if v]
    if include_suggestions:
        result["suggestions"] = await run_in_threadpool(get_suggestions, text, jd_text, result)
    return result
