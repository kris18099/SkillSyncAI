from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.roadmap_generator import StructuredRoadmap, generate_roadmap_with_claude

router = APIRouter(tags=["roadmap"])


class RoadmapGenerateRequest(BaseModel):
    candidate_skills: List[str]
    missing_skills: List[str]
    target_role: str = "Software Engineer"


@router.post("/roadmap/generate", response_model=StructuredRoadmap)
def generate_roadmap_endpoint(payload: RoadmapGenerateRequest) -> StructuredRoadmap:
    return generate_roadmap_with_claude(
        candidate_skills=payload.candidate_skills,
        missing_skills=payload.missing_skills,
        target_role=payload.target_role
    )
