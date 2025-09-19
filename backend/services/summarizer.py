from transformers import pipeline
from services.db_manager import get_paper 

# 서버 시작 시 모델 로딩 (변경 없음)
_summarizer = pipeline("summarization", model="google/pegasus-pubmed")

def _summarize_text(text: str, max_len: int = 200, min_len: int = 30) -> str:
    """실제 요약 수행 (짧은 텍스트는 그대로 반환) (변경 없음)"""
    if not text or len(text.split()) < 30:
        return text
    
    summary = _summarizer(
        text, max_length=max_len, min_length=min_len, do_sample=False
    )
    return summary[0]['summary_text']

def get_summary(pmid: str, text_to_summarize: str) -> str:
    # 1. DB에서 pmid로 캐시 확인
    cached = get_paper(pmid)
    if cached and cached.get("summary"):
        return cached["summary"]

    # 2. 캐시가 없으면 새로 요약 생성
    summary = _summarize_text(text_to_summarize)
    
    # 3. DB에 저장하지 않고, 요약 텍스트만 반환
    return summary
