# SkillSync AI

SkillSync AI turns a student's resume into a tailored skill-gap analysis and week-by-week learning roadmap based on real job postings.

## Build status

Phase 1 is implemented: PDF, DOCX, DOC, RTF, and ODT resume uploads are parsed into raw text through a FastAPI endpoint. Later phases will add Claude skill extraction, job-posting embeddings, tailored gap scoring, roadmap generation, and the React interface.

## Phase 1 — run locally

From the `backend` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

Upload a PDF, DOCX, DOC, RTF, or ODT file to `POST /api/resumes/parse` using the `file` form field. The response contains `filename`, `text`, and `character_count`.

The parser is deliberately isolated in `app/services/resume_parser.py` so later AI, persistence, and indexing layers can be added without changing upload behavior.