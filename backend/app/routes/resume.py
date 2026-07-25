from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.resume_parser import UnsupportedResumeType, extract_resume_text
from app.services.skill_extractor import ExtractedSkillProfile, extract_skills_with_claude

router = APIRouter(tags=["resumes"])


class TextParseRequest(BaseModel):
    text: str


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/resumes/parse")
async def parse_resume(file: UploadFile = File(...)) -> dict[str, str | int]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the 5 MB maximum limit."
        )

    try:
        text = extract_resume_text(file.filename, content)
    except UnsupportedResumeType as error:
        raise HTTPException(status_code=415, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=422, detail="Could not extract resume text.") from error

    if not text:
        raise HTTPException(status_code=422, detail="No readable text was found in the resume.")

    return {"filename": file.filename, "text": text, "character_count": len(text)}


@router.post("/resumes/extract-skills", response_model=ExtractedSkillProfile)
async def extract_skills_from_text(payload: TextParseRequest) -> ExtractedSkillProfile:
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text content cannot be empty.")
    return extract_skills_with_claude(payload.text)


@router.post("/resumes/upload-and-extract", response_model=dict)
async def upload_and_extract(file: UploadFile = File(...)) -> dict:
    parse_res = await parse_resume(file)
    resume_text = parse_res["text"]
    profile = extract_skills_with_claude(resume_text)
    return {
        "filename": parse_res["filename"],
        "character_count": parse_res["character_count"],
        "raw_text": resume_text,
        "profile": profile.model_dump()
    }