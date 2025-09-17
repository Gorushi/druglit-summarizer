from fastapi import APIRouter, HTTPException, Query
from models.paper import SearchResult, Paper
from services.pubmed_client import search_pubmed, fetch_pubmed_abstract
from services.summarizer import get_summary
from services.db_manager import get_papers_by_drug, save_paper 
from datetime import datetime

router = APIRouter()

@router.get("/search", response_model=SearchResult)
def search(drug: str = Query(..., description="약물명 (영어로 입력)")):
    # 1. DB에서 먼저 최신 논문을 가져옴 (DB가 정렬/제한을 처리)
    papers_from_db = get_papers_by_drug(drug)
    existing_pmids = {p['pmid'] for p in papers_from_db}

    # 2. PubMed에서 최신 pmid 목록을 가져옴
    pmid_list_from_pubmed = search_pubmed(drug, retmax=30)
    if not pmid_list_from_pubmed:
        # DB에 결과가 있을 수 있으므로 바로 404를 보내지 않음
        if not papers_from_db:
            raise HTTPException(status_code=404, detail="검색 결과 없음")
        return SearchResult(drug=drug, papers=[Paper(**p) for p in papers_from_db])

    # 3. DB에 없는 새로운 pmid만 추려냄
    new_pmids_to_process = [pmid for pmid in pmid_list_from_pubmed if pmid not in existing_pmids]

    # 4. 새로운 논문에 대해서만 작업을 수행
    newly_added_papers = []
    for pmid in new_pmids_to_process:
        info = fetch_pubmed_abstract(pmid)
        if not info or "abstract" not in info:
            continue

        pubdate_str = _parse_pubdate(info.get("pubdate", "")) # str | None 반환
        
        summary = get_summary(pmid, info["abstract"])
        
        paper_dict = {
            "pmid": pmid,
            "drug": drug,
            "title": info.get("title", ""),
            "abstract": info["abstract"],
            "summary": summary,
            "pubdate": pubdate_str, # DB와 모델 모두 str 타입으로 일관성 유지
        }
        save_paper(paper_dict)
        newly_added_papers.append(paper_dict)

    # 5. 기존 결과와 새로운 결과를 합쳐 최종 응답을 생성
    final_papers = papers_from_db + newly_added_papers
    
    # pubdate가 없는 경우를 대비하여 안전하게 정렬 (문자열 '0000'은 오래된 날짜로 취급됨)
    final_papers.sort(key=lambda p: p.get('pubdate') or '0000', reverse=True)
    
    # Pydantic 모델로 변환하여 최종 15개만 반환
    papers_response = [Paper(**p) for p in final_papers[:15]]

    return SearchResult(drug=drug, papers=papers_response)

def _parse_pubdate(date_str: str) -> str | None:
    """PubMed 날짜 포맷 여러 형태 처리 -> ISO8601 문자열(YYYY-MM-DD) 또는 None 반환"""
    if not date_str:
        return None
    # 다양한 날짜 형식을 시도하여 파싱
    for fmt in ("%Y-%m-%d", "%Y %b %d", "%Y %b", "%Y"):
        try:
            # .split(' ')[0] 부분을 삭제하여 전체 문자열을 파싱하도록 변경
            return datetime.strptime(date_str, fmt).date().isoformat()
        except ValueError:
            continue
    # 뒤에 추가 정보가 붙기도 함
    # 이런 경우를 대비해 첫 부분만 다시 시도
    for fmt in ("%Y-%m-%d", "%Y %b %d", "%Y %b", "%Y"):
        try:
            # 예외 처리: 첫 번째 단어만으로 다시 시도
            return datetime.strptime(date_str.split(' ')[0], fmt).date().isoformat()
        except ValueError:
            continue

    return None
