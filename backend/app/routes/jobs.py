from typing import List, Optional
from fastapi import APIRouter, Query

from app.services.job_indexer import search_jobs

router = APIRouter(tags=["jobs"])


@router.get("/jobs/search")
def search_job_postings(
    query: str = Query(..., description="Query string for skill or role"),
    role: Optional[str] = Query(None, description="Optional role category filter"),
    top_k: int = Query(5, ge=1, le=50)
) -> List[dict]:
    return search_jobs(query=query, top_k=top_k, role_filter=role)
