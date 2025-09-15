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
    drug_cache = cache.get(drug, {})  # drug 단위 캐싱

    papers = []

    for pmid in pmid_list:
        if pmid in drug_cache:
            # 이미 캐시되어 있으면 그대로 사용
            papers.append(Paper(**drug_cache[pmid]))
            continue

        info = fetch_pubmed_abstract(pmid)
        if not info:
            continue

        # 날짜 파싱
        pubdate_str = info.get("pubdate", "1900")
        pubdate = _parse_pubdate(pubdate_str)

        # 요약 + 캐싱
        summary = summarize_with_cache(
            drug=drug,
            pmid=pmid,
            title=info.get("title"),
            text=info.get("abstract"),
            pubdate=pubdate,
        )

        paper = Paper(
            pmid=pmid,
            title=info.get("title"),
            abstract=info.get("abstract"),
            summary=summary,
            pubdate=pubdate
        )

        # drug_cache 갱신
        drug_cache[pmid] = paper.dict()

    # 전체 cache에 drug_cache 반영 후 저장
    cache[drug] = drug_cache
    save_cache(cache)

    # 최신순 정렬 & 상위 15개만 반환
    papers = [Paper(**p) for p in drug_cache.values()]
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

