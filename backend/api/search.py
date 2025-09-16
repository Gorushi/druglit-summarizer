from fastapi import APIRouter, HTTPException, Query
from models.paper import SearchResult, Paper
from services.pubmed_client import search_pubmed, fetch_pubmed_abstract
from services.summarizer import summarize_with_cache
from services.cache_manager import load_cache, save_cache
from datetime import datetime, date

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
    drug_cache = cache.get(drug, {})  # drug 단위 캐싱

    papers = []

    for pmid in pmid_list:
        if pmid in drug_cache:
            papers.append(Paper(**drug_cache[pmid]))
            continue

        info = fetch_pubmed_abstract(pmid)
        if not info:
            continue

        # pubdate 파싱 (없으면 None)
        pubdate_str = info.get("pubdate", "")
        pubdate = _parse_pubdate(pubdate_str)

        summary = summarize_with_cache(
            drug=drug,
            pmid=pmid,
            title=info.get("title"),
            text=info["abstract"],  
            pubdate=pubdate,
        )

        paper = Paper(
            pmid=pmid,
            title=info.get("title", ""),  # title 없으면 빈 문자열
            abstract=info["abstract"],
            summary=summary,
            pubdate=pubdate
        )

        drug_cache[pmid] = paper.dict()

    cache[drug] = drug_cache
    save_cache(cache)

    # 최신순 정렬 & 상위 15개만 반환
    papers = [Paper(**p) for p in drug_cache.values()]
    papers.sort(key=lambda p: p.pubdate or date.min, reverse=True)
    papers = papers[:15]

    return SearchResult(drug=drug, papers=papers)


def _parse_pubdate(date_str: str):
    """PubMed 날짜 포맷 여러 형태 처리 (없으면 None 반환)"""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y %b %d", "%Y %b", "%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

