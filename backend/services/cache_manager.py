import json
from datetime import date
from pathlib import Path
from typing import Dict, Any

CACHE_FILE = Path("cache.json")

def load_cache() -> Dict[str, Dict[str, Any]]:
    """
    캐시 파일 로드.
    {
        "drugA": {
            "pmid1": { "pmid": "...", "abstract": "...", "summary": "...", "pubdate": date(...) },
            "pmid2": { ... }
        },
        "drugB": { ... }
    }
    """
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
            # pubdate 문자열을 date 객체로 변환
            for drug, papers in cache.items():
                for pmid, p in papers.items():
                    if "pubdate" in p and isinstance(p["pubdate"], str):
                        p["pubdate"] = date.fromisoformat(p["pubdate"])
            return cache
    except FileNotFoundError:
        return {}

def save_cache(cache: Dict[str, Dict[str, Any]]):
    """전체 캐시 저장 (pubdate는 문자열로 변환)"""
    serializable_cache = {}
    for drug, papers in cache.items():
        serializable_cache[drug] = {}
        for pmid, p in papers.items():
            serializable_cache[drug][pmid] = {
                **p,
                "pubdate": p["pubdate"].isoformat() if isinstance(p["pubdate"], date) else p["pubdate"]
            }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable_cache, f, ensure_ascii=False, indent=2)

