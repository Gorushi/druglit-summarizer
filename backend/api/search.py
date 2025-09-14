from fastapi import APIRouter, HTTPException, Query
from models.paper import SearchResult, Paper
from services.pubmed_client import search_pubmed, fetch_pubmed_abstract
from services.summarizer import summarize_with_cache
from services.cache_manager import load_cache, save_cache
from datetime import datetime

router = APIRouter()

@router.get("/search", response_model=SearchResult)
def search(drug: str = Query(..., description="약물명 (영어로 입력)")):
    """
    약물 이름으로 PubMed에서 최신 논문 검색 → 요약 + 캐싱
    """
    pmid_list = search_pubmed(drug, retmax=30)
    if not pmid_list:
        raise HTTPException(status_code=404, detail="검색 결과 없음")

    cache = load_cache()
    cached_papers = cache.get(drug, [])
    papers = []

    for pmid in pmid_list:
        # 캐시 확인
        if pmid in cache:
            papers.append(Paper(**cache[pmid]))
            continue

        info = fetch_pubmed_abstract(pmid)
        if not info:
            continue

        # 날짜 파싱
        pubdate_str = info.get("pubdate", "1900")
        pubdate = _parse_pubdate(pubdate_str)

        summary = summarize_with_cache(drug, pmid, info.get("abstract"))

        paper = Paper(
            pmid=pmid,
            title=info.get("title"),
            abstract=info.get("abstract"),
            summary=summary,
            pubdate=pubdate
        )

        save_cache(drug, paper.dict())
        papers.append(paper)

    papers.sort(key=lambda p: p.pubdate, reverse=True)
    papers = papers[:15]

    return SearchResult(drug=drug, papers=papers)


def _parse_pubdate(date_str: str):
    """PubMed 날짜 포맷 여러 형태 처리"""
    for fmt in ("%Y %b %d", "%Y %b", "%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            continue
    return datetime(1900, 1, 1).date()

