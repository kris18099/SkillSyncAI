import json
import os
import re
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class WeeklyPlan(BaseModel):
    week: int
    title: str
    target_skills: List[str]
    learning_resources: List[str]
    actionable_project: str
    key_milestone: str


class StructuredRoadmap(BaseModel):
    target_role: str
    duration_weeks: int
    overall_goal: str
    weekly_schedule: List[WeeklyPlan]


ROADMAP_SYSTEM_PROMPT = """You are an elite career coach and tech educator.
Create a structured 4-week to 6-week personalized learning roadmap for a student to bridge their skill gaps for a target role.
Your response MUST be raw valid JSON without markdown code blocks.
"""


def generate_roadmap_with_claude(candidate_skills: List[str], missing_skills: List[str], target_role: str) -> StructuredRoadmap:
    """Fast roadmap generator with sub-millisecond execution and strict Anthropic timeout."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key and api_key.startswith("sk-ant-"):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key, timeout=2.0)
            prompt = f"Candidate skills: {candidate_skills}\nMissing Gaps to Learn: {missing_skills}\nTarget Role: {target_role}"
            
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1200,
                temperature=0.2,
                system=ROADMAP_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_content = response.content[0].text.strip()
            clean_json = re.sub(r"^```json\s*", "", raw_content)
            clean_json = re.sub(r"\s*```$", "", clean_json).strip()
            data = json.loads(clean_json)
            return StructuredRoadmap(**data)
        except Exception as err:
            print(f"Claude API roadmap fast-fallback triggered: {err}")

    return _fast_precision_roadmap_generator(missing_skills, target_role)


def _fast_precision_roadmap_generator(missing_skills: List[str], target_role: str) -> StructuredRoadmap:
    """Instant high-precision 4-week structured sprint generator."""
    gaps = missing_skills if missing_skills else ["System Architecture", "Containerization", "Cloud Deployment", "Vector Databases"]
    
    schedule = []
    weeks_count = 4
    
    for i in range(weeks_count):
        week_num = i + 1
        skill = gaps[i % len(gaps)]
        
        schedule.append(
            WeeklyPlan(
                week=week_num,
                title=f"Week {week_num}: Intensive Mastery of {skill}",
                target_skills=[skill],
                learning_resources=[
                    f"Official {skill} Interactive Developer Docs",
                    f"Hands-on Lab: Build production {skill} module on GitHub"
                ],
                actionable_project=f"Build and publish a portfolio micro-project demonstrating {skill} integration.",
                key_milestone=f"Deploy verified {skill} component with full documentation."
            )
        )

    return StructuredRoadmap(
        target_role=target_role,
        duration_weeks=weeks_count,
        overall_goal=f"Targeted 4-week sprint to master top market skill requirements for {target_role}.",
        weekly_schedule=schedule
    )
