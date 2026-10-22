"""Step 1: turn an uploaded resume (PDF/DOCX) into clean text and sections."""
import io
import re
from pathlib import Path

SECTION_HEADERS = {
    "skills": ["skills", "technical skills", "key skills", "core competencies"],
    "education": ["education", "academic background", "academics"],
    "experience": ["experience", "work experience", "internship", "internships",
                   "professional experience"],
    "projects": ["projects", "academic projects", "personal projects"],
}


def extract_text_from_bytes(data: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        import fitz  # PyMuPDF
        with fitz.open(stream=data, filetype="pdf") as doc:
            text = "\n".join(page.get_text("text") for page in doc)
    elif suffix == ".docx":
        import docx
        document = docx.Document(io.BytesIO(data))
        text = "\n".join(p.text for p in document.paragraphs)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    return clean_text(text)


def extract_text(path: str) -> str:
    p = Path(path)
    return extract_text_from_bytes(p.read_bytes(), p.name)


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[•●▪◦►■]", "-", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_sections(text: str) -> dict:
    """Group lines under the most recent recognised heading."""
    lookup = {h: sec for sec, hs in SECTION_HEADERS.items() for h in hs}
    sections = {"header": []}
    current = "header"
    for line in text.splitlines():
        key = line.strip().rstrip(":").lower()
        if key in lookup:
            current = lookup[key]
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}
