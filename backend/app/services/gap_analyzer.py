from collections import Counter
from typing import Any, Dict, List
from pydantic import BaseModel, Field

from app.services.job_indexer import search_jobs


class SkillGapItem(BaseModel):
    skill: str
    frequency_count: int
    demand_percentage: float
    importance_level: str = "High"


class SkillGapAnalysisResult(BaseModel):
    target_role: str
    total_matched_jobs: int
    candidate_skills: List[str]
    missing_skills_ranked: List[SkillGapItem]
    matching_skills: List[str]
    match_score_percentage: float
    summary: str


def analyze_skill_gaps(candidate_skills: List[str], target_role: str = "Software Engineer", top_k_jobs: int = 15) -> SkillGapAnalysisResult:
    """
    Retrieves top_k_jobs for target_role using FAISS index,
    computes frequency of required skills, ranks missing candidate skills.
    """
    # 1. Search FAISS index for relevant job postings
    query_str = f"{target_role} required skills: {', '.join(candidate_skills)}"
    matched_jobs = search_jobs(query=query_str, top_k=top_k_jobs, role_filter=target_role)
    
    if not matched_jobs:
        # Fallback search without strict role filter if needed
        matched_jobs = search_jobs(query=query_str, top_k=top_k_jobs)

    total_jobs = len(matched_jobs) if matched_jobs else 1
    
    # 2. Count skill frequencies across matching postings
    skill_counter = Counter()
    candidate_skills_lower = {s.strip().lower() for s in candidate_skills}

    for job in matched_jobs:
        for req_skill in job.get("required_skills", []):
            skill_counter[req_skill.strip()] += 1

    # 3. Separate candidate skills vs missing skills
    missing_items: List[SkillGapItem] = []
    matching_skills: List[str] = []

    for skill_name, count in skill_counter.most_common():
        skill_lower = skill_name.lower()
        
        # Check if candidate has skill
        if any(c_skill == skill_lower or c_skill in skill_lower or skill_lower in c_skill for c_skill in candidate_skills_lower):
            matching_skills.append(skill_name)
        else:
            pct = round((count / total_jobs) * 100, 1)
            importance = "High" if pct >= 60 else ("Medium" if pct >= 35 else "Low")
            missing_items.append(
                SkillGapItem(
                    skill=skill_name,
                    frequency_count=count,
                    demand_percentage=pct,
                    importance_level=importance
                )
            )

    # 4. Calculate overall match percentage
    total_unique_market_skills = len(skill_counter) if skill_counter else 1
    matched_count = len(matching_skills)
    match_pct = round((matched_count / total_unique_market_skills) * 100, 1) if total_unique_market_skills > 0 else 50.0

    return SkillGapAnalysisResult(
        target_role=target_role,
        total_matched_jobs=total_jobs,
        candidate_skills=candidate_skills,
        missing_skills_ranked=missing_items,
        matching_skills=list(dict.fromkeys(matching_skills)),
        match_score_percentage=min(100.0, max(10.0, match_pct)),
        summary=f"Analyzed {total_jobs} active postings for {target_role}. Identified {len(missing_items)} priority skill gaps."
    )
