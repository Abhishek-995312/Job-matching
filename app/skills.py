"""Step 2: dictionary-based skill extraction with alias normalisation."""
import json
import re
from functools import lru_cache
from pathlib import Path

SKILLS_PATH = Path(__file__).resolve().parent.parent / "data" / "skills.json"


@lru_cache(maxsize=1)
def _patterns():
    skills = json.loads(SKILLS_PATH.read_text(encoding="utf-8"))
    compiled = []
    for canonical, aliases in skills.items():
        for alias in aliases:
            # custom boundaries so "c++" style tokens work
            pat = r"(?<![\w+#])" + re.escape(alias) + r"(?![\w+#])"
            compiled.append((canonical, re.compile(pat, re.IGNORECASE)))
    return compiled


def extract_skills(text: str) -> set:
    return {canonical for canonical, pat in _patterns() if pat.search(text)}
