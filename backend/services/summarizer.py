import logging
from transformers import pipeline, Pipeline
from services.cache_manager import load_cache, save_cache

try:
    summarizer: Pipeline = pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        tokenizer="facebook/bart-large-cnn"
    )
    logging.info("✅ Summarizer model loaded successfully.")
except Exception as e:
    summarizer = None
    logging.error(f"⚠️ Failed to load summarizer: {e}")


def summarize_with_cache(drug: str, pmid: str, text: str, max_len: int = 200, min_len: int = 30) -> str:
    if not text:
        return ""

    cache = load_cache()  # 전체 캐시 로드
    drug_cache = cache.get(drug, {})  # drug별 데이터만 추출

    if pmid in drug_cache and drug_cache[pmid].get("summary"):
        return drug_cache[pmid]["summary"]

    if len(text.split()) < 30:
        summary = text
    else:
        summary = _summarize_text(text, max_len, min_len)

    # drug_cache 업데이트
    drug_cache[pmid] = {
        "pmid": pmid,
        "abstract": text,
        "summary": summary,
    }
    cache[drug] = drug_cache  # 전체 캐시에 반영

    save_cache(cache)  # 전체 캐시 저장

    return summary

def _summarize_text(text: str, max_len: int, min_len: int) -> str:
    if summarizer is None:
        logging.warning("Summarizer unavailable, returning original text.")
        return text
    try:
        result = summarizer(
            text,
            max_length=max_len,
            min_length=min_len,
            do_sample=False,
            truncation=True
        )
        return result[0].get("summary_text", text)
    except Exception as e:
        logging.error(f"Summarization failed: {e}")
        return text

