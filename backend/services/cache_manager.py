import json
import os
from datetime import datetime
from typing import List, Dict, Any

CACHE_FILE = "pubmed_cache.json"

def _load_cache() -> Dict[str, Any]:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_cache(cache: Dict[str, Any]):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_cached_results(drug_name: str) -> List[Dict[str, Any]]:
    cache = _load_cache()
    return cache.get(drug_name.lower(), [])

def update_cache(drug_name: str, new_results: List[Dict[str, Any]]):
    cache = _load_cache()
    drug_key = drug_name.lower()
    existing = cache.get(drug_key, [])

    # 중복 제거 (pubmed_id 기준)
    existing_ids = {item["pubmed_id"] for item in existing}
    merged = existing + [r for r in new_results if r["pubmed_id"] not in existing_ids]

    # 최신순 정렬 후 최대 15개만 유지
    merged.sort(key=lambda x: x["pub_date"], reverse=True)
    cache[drug_key] = merged[:15]

    _save_cache(cache)

