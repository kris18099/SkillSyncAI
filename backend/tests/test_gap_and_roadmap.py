from app.services.gap_analyzer import analyze_skill_gaps
from app.services.roadmap_generator import generate_roadmap_with_claude


def test_skill_gap_analysis_data_analyst():
    candidate_skills = ["Python", "SQL", "Excel"]
    result = analyze_skill_gaps(candidate_skills, target_role="Data Analyst")
    
    assert result is not None
    assert result.target_role == "Data Analyst"
    assert len(result.missing_skills_ranked) > 0
    # Expected gaps like Tableau or Power BI or Pandas
    gap_skills = [item.skill for item in result.missing_skills_ranked]
    assert any(g in gap_skills for g in ["Tableau", "Power BI", "Pandas", "Statistics", "A/B Testing", "ETL"])


def test_roadmap_generation():
    candidate_skills = ["Python", "FastAPI"]
    missing_skills = ["Docker", "PostgreSQL", "React"]
    roadmap = generate_roadmap_with_claude(candidate_skills, missing_skills, target_role="Software Engineer")
    
    assert roadmap is not None
    assert roadmap.duration_weeks >= 3
    assert len(roadmap.weekly_schedule) >= 3
    first_week = roadmap.weekly_schedule[0]
    assert first_week.week == 1
    assert len(first_week.actionable_project) > 0
