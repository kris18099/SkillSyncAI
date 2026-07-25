import pytest
from app.services.skill_extractor import extract_skills_with_claude

RESUME_DATA_ANALYST = """
Alex Rivera - Data Analyst
Experience:
- Analyzed large datasets using Python, Pandas, and SQL to drive business intelligence.
- Built interactive dashboards in Tableau and Power BI for executive leadership.
- Experienced with Excel advanced formulas, pivot tables, and statistical modeling.
Projects:
- Customer Churn Prediction: Modeled churn using Scikit-Learn and Python.
"""

RESUME_GENAI_ENGINEER = """
Samantha Lee - Generative AI Engineer
Experience:
- Developed LLM applications using PyTorch, FastAPI, and LangChain.
- Built RAG pipelines using FAISS vector search and OpenAI / Claude embeddings.
- Deployed containerized microservices on AWS Docker.
Projects:
- Enterprise Knowledge Bot: Integrated Claude API with vector database for QA over documents.
"""

RESUME_FULLSTACK = """
Jordan Smith - Software Engineer
Experience:
- 4 years building scalable web apps with React, TypeScript, FastAPI, and PostgreSQL.
- Designed REST APIs and implemented Docker container workflows.
- Strong knowledge of Git, CI/CD, and HTML/CSS/Tailwind.
"""


def test_extract_skills_data_analyst():
    profile = extract_skills_with_claude(RESUME_DATA_ANALYST)
    assert profile is not None
    assert len(profile.skills) > 0
    assert any(s.lower() in ["python", "sql", "pandas", "tableau", "excel"] for s in profile.skills)
    assert profile.target_role_recommendation == "Data Analyst"


def test_extract_skills_genai_engineer():
    profile = extract_skills_with_claude(RESUME_GENAI_ENGINEER)
    assert profile is not None
    assert len(profile.skills) > 0
    assert any(s.lower() in ["pytorch", "fastapi", "faiss", "llm", "python"] for s in profile.skills)
    assert profile.target_role_recommendation == "Generative AI Engineer"


def test_extract_skills_fullstack():
    profile = extract_skills_with_claude(RESUME_FULLSTACK)
    assert profile is not None
    assert len(profile.skills) > 0
    assert any(s.lower() in ["react", "fastapi", "postgresql", "docker", "typescript"] for s in profile.skills)
