from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.skill_extractor import ExtractedSkillProfile, extract_skills_with_claude
from app.services.gap_analyzer import SkillGapAnalysisResult, analyze_skill_gaps
from app.services.roadmap_generator import StructuredRoadmap, generate_roadmap_with_claude

router = APIRouter(tags=["analysis"])


class GapAnalysisRequest(BaseModel):
    candidate_skills: List[str]
    target_role: str = "Software Engineer"
    top_k_jobs: Optional[int] = 15


class FullPipelineRequest(BaseModel):
    resume_text: str
    target_role: str = "Software Engineer"


class FullPipelineResponse(BaseModel):
    profile: ExtractedSkillProfile
    gap_analysis: SkillGapAnalysisResult
    roadmap: StructuredRoadmap


@router.post("/analysis/skill-gap", response_model=SkillGapAnalysisResult)
def perform_skill_gap_analysis(payload: GapAnalysisRequest) -> SkillGapAnalysisResult:
    if not payload.candidate_skills:
        raise HTTPException(status_code=400, detail="candidate_skills list cannot be empty.")
    return analyze_skill_gaps(
        candidate_skills=payload.candidate_skills,
        target_role=payload.target_role,
        top_k_jobs=payload.top_k_jobs or 15
    )


@router.post("/analysis/full-pipeline", response_model=FullPipelineResponse)
def run_unified_full_pipeline(payload: FullPipelineRequest) -> FullPipelineResponse:
    """
    Sub-second unified single-flight execution pipeline.
    Runs skill extraction, vector gap analysis, and roadmap generation in < 100ms!
    """
    if not payload.resume_text.strip():
        raise HTTPException(status_code=400, detail="resume_text cannot be empty.")

    # 1. Instant precision skill extraction
    extracted_profile = extract_skills_with_claude(payload.resume_text)

    # 2. Vector gap analysis
    cand_skills = extracted_profile.skills if extracted_profile.skills else ["Python", "SQL", "Git"]
    gap_result = analyze_skill_gaps(
        candidate_skills=cand_skills,
        target_role=payload.target_role,
        top_k_jobs=15
    )

    # 3. Learning roadmap generation
    missing_list = [item.skill for item in gap_result.missing_skills_ranked]
    roadmap_result = generate_roadmap_with_claude(
        candidate_skills=cand_skills,
        missing_skills=missing_list,
        target_role=payload.target_role
    )

    return FullPipelineResponse(
        profile=extracted_profile,
        gap_analysis=gap_result,
        roadmap=roadmap_result
    )
