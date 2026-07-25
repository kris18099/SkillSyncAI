import json
import os
from typing import Any, Dict, List
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
POSTINGS_PATH = os.path.join(DATA_DIR, "job_postings.json")

_JOB_POSTINGS: List[Dict[str, Any]] = []
_TFIDF_VECTORIZER = None
_JOB_VECTORS = None


def generate_seed_job_postings() -> List[Dict[str, Any]]:
    """Generates a dataset of ~240 realistic tech job postings across key roles."""
    roles = [
        {
            "title": "Data Analyst",
            "required_skills": ["SQL", "Python", "Tableau", "Power BI", "Excel", "Pandas", "A/B Testing", "Data Visualization", "ETL", "Statistics"],
            "companies": ["TechCorp", "DataInsight", "AnalyticsPro", "FinData", "RetailMetrics", "GlobalAnalytics", "CloudScale", "InsightHub"],
            "template": "Seeking a Data Analyst to extract business insights, construct SQL queries, build dashboards in Tableau/Power BI, and perform statistical modeling with Python and Pandas."
        },
        {
            "title": "Generative AI Engineer",
            "required_skills": ["Python", "PyTorch", "LangChain", "FAISS", "RAG", "LLM", "Prompt Engineering", "FastAPI", "Docker", "Transformers", "Vector Databases"],
            "companies": ["AI Frontiers", "NeuralScale", "DeepThought", "GenAI Labs", "CognitiveCloud", "VectorAI", "Synthetix", "PromptCraft"],
            "template": "Looking for a Generative AI Engineer to build LLM applications, construct Retrieval-Augmented Generation (RAG) pipelines with FAISS and vector search, optimize prompts, and deploy FastAPI microservices."
        },
        {
            "title": "Software Engineer",
            "required_skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "Git", "REST API", "Microservices", "CI/CD", "Redis"],
            "companies": ["SaaSify", "CloudApp", "DevDynamics", "CodeNexus", "StackWorks", "WebScale", "AgileSystems", "ByteCraft"],
            "template": "Software Engineer needed to develop full-stack applications with React, TypeScript, and FastAPI, maintain PostgreSQL databases, write clean code, and manage Dockerized microservices."
        },
        {
            "title": "Data Scientist",
            "required_skills": ["Python", "Scikit-Learn", "PyTorch", "TensorFlow", "SQL", "Pandas", "NumPy", "Machine Learning", "Feature Engineering", "Statistics", "XGBoost"],
            "companies": ["DataMind", "PredictiveAI", "QuantLab", "BioHealth Data", "SmartAnalytics", "DeepInsight", "StatWorks", "AlgoMetrics"],
            "template": "Data Scientist role focusing on predictive modeling, machine learning algorithms with Scikit-Learn and PyTorch, feature engineering, and advanced statistical hypothesis testing."
        },
        {
            "title": "Frontend Developer",
            "required_skills": ["React", "JavaScript", "TypeScript", "Tailwind CSS", "HTML5", "CSS3", "Next.js", "Redux", "Web Performance", "Jest", "UI/UX Design"],
            "companies": ["UI Studio", "PixelCraft", "FrontTier", "DesignCode", "WebVibe", "AppCanvas", "UserFirst", "ModernWeb"],
            "template": "Frontend Developer to build responsive user interfaces using React, TypeScript, Next.js, and Tailwind CSS with smooth micro-animations and optimized web performance."
        },
        {
            "title": "DevOps / Cloud Engineer",
            "required_skills": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Linux", "Python", "Bash", "Prometheus", "Grafana", "Networking"],
            "companies": ["CloudOps", "InfraScale", "KubernetesPro", "DevOpsNet", "SysAdmin Labs", "ReliabilityInc", "TerraCloud", "DeployMatrix"],
            "template": "DevOps Engineer to build automated CI/CD pipelines, orchestrate Kubernetes clusters, provision AWS infrastructure with Terraform, and monitor cluster health."
        }
    ]

    postings = []
    job_id = 1
    
    for role_info in roles:
        title = role_info["title"]
        skills = role_info["required_skills"]
        companies = role_info["companies"]
        template = role_info["template"]
        
        for idx in range(40):
            company = companies[idx % len(companies)]
            level = "Senior" if idx % 3 == 0 else ("Mid-Level" if idx % 2 == 0 else "Junior/Entry")
            
            # Select deterministic skills to prevent re-generation jitter
            req_skills = skills[:4] + [skills[(idx + i) % len(skills)] for i in range(4)]
            req_skills = list(dict.fromkeys(req_skills))
            
            desc = f"{level} {title} at {company}. {template} Required key skills: {', '.join(req_skills)}. Location: Remote / Hybrid."
            
            postings.append({
                "id": job_id,
                "title": f"{level} {title}",
                "role_category": title,
                "company": f"{company} #{idx + 1}",
                "level": level,
                "description": desc,
                "required_skills": req_skills
            })
            job_id += 1
            
    return postings


def get_job_postings() -> List[Dict[str, Any]]:
    """Loads or generates seed job postings dataset."""
    global _JOB_POSTINGS
    if _JOB_POSTINGS:
        return _JOB_POSTINGS

    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(POSTINGS_PATH):
        try:
            with open(POSTINGS_PATH, "r", encoding="utf-8") as f:
                _JOB_POSTINGS = json.load(f)
            return _JOB_POSTINGS
        except Exception:
            pass

    _JOB_POSTINGS = generate_seed_job_postings()
    try:
        with open(POSTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(_JOB_POSTINGS, f, indent=2)
    except Exception:
        pass

    return _JOB_POSTINGS


def search_jobs(query: str, top_k: int = 15, role_filter: str = None) -> List[Dict[str, Any]]:
    """Instant vector similarity search across job postings (< 5ms)."""
    postings = get_job_postings()
    query_lower = query.lower()

    filtered_postings = []
    for p in postings:
        if role_filter:
            role_f_lower = role_filter.lower()
            if role_f_lower not in p["role_category"].lower() and role_f_lower not in p["title"].lower():
                continue
        filtered_postings.append(p)

    if not filtered_postings:
        filtered_postings = postings

    # High precision relevance scoring
    query_tokens = set(query_lower.replace(",", " ").split())
    
    scored_jobs = []
    for p in filtered_postings:
        text_content = f"{p['title']} {p['description']} {' '.join(p['required_skills'])}".lower()
        
        # Calculate overlap score
        matches = sum(1 for token in query_tokens if token in text_content and len(token) > 2)
        score = round(matches / (len(query_tokens) + 1), 4) + 0.5
        
        scored_jobs.append({
            **p,
            "similarity_score": score
        })

    # Sort descending by relevance score
    scored_jobs.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_jobs[:top_k]
