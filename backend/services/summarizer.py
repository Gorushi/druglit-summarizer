from transformers import pipeline
from datetime import date
from services.cache_manager import load_cache, save_cache

# 서버 시작 시 모델 로딩 (한 번만)
_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def _summarize_text(text: str, max_len: int = 200, min_len: int = 30) -> str:
    """실제 요약 수행 (짧은 텍스트는 그대로 반환)"""
    if not text or len(text.split()) < 30:
        return text

    summary = _summarizer(
        text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False
    )
    return summary[0]['summary_text']

def summarize_with_cache(drug: str, pmid: str, title: str, text: str, pubdate: date, max_len: int = 200, min_len: int = 30) -> str:
    """
    약물 이름(drug), PMID, 제목(title), 원문(text), pubdate 기반 요약 + 캐싱
    - 캐시에 summary가 있으면 재사용
    - 없으면 새로 요약 후 캐시에 저장
    """
    cache = load_cache()
    drug_cache = cache.get(drug, {})

    # 캐시에 요약이 있으면 그대로 반환
    if pmid in drug_cache and drug_cache[pmid].get("summary"):
        return drug_cache[pmid]["summary"]

    # 요약 수행
    summary = text if len(text.split()) < 30 else _summarize_text(text, max_len, min_len)
    
    # title 필드 포함해서 캐싱
    drug_cache[pmid] = {
        "pmid": pmid,
        "title": title,                   
        "abstract": text,
        "summary": summary,
        "pubdate": pubdate.isoformat(),   # date → str 직렬화
    }
    
    cache[drug] = drug_cache
    save_cache(cache)
    
    return summary

