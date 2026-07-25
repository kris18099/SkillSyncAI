from app.services.job_indexer import get_job_postings, search_jobs


def test_job_indexer_initialization():
    postings = get_job_postings()
    assert len(postings) >= 200


def test_job_similarity_search_data_analyst():
    results = search_jobs(query="SQL Tableau dashboards statistics", top_k=5, role_filter="Data Analyst")
    assert len(results) > 0
    top_result = results[0]
    assert "Data Analyst" in top_result["role_category"] or "Data Analyst" in top_result["title"]
    assert any(skill in top_result["required_skills"] for skill in ["SQL", "Tableau", "Power BI", "Excel", "Python"])


def test_job_similarity_search_genai():
    results = search_jobs(query="PyTorch LangChain FAISS RAG vector search LLM", top_k=5, role_filter="Generative AI Engineer")
    assert len(results) > 0
    top_result = results[0]
    assert "Generative AI Engineer" in top_result["role_category"] or "AI" in top_result["title"]
    assert top_result["similarity_score"] > 0
