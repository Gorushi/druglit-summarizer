import json
from datetime import date

CACHE_FILE = "cache.json"

def _get_cache_file(drug: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{drug.lower()}.json")

def load_cache():
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
            # 날짜 문자열을 다시 date 객체로 변환
            for drug, papers in cache.items():
                for p in papers:
                    if "pubdate" in p:
                        p["pubdate"] = date.fromisoformat(p["pubdate"])
            return cache
    except FileNotFoundError:
        return {}

def save_cache(drug: str, paper_dict: dict):
    cache = load_cache()
    if drug not in cache:
        cache[drug] = []
    # 이미 같은 title+date 조합이 있는지 확인 후 중복 방지
    if not any(p["title"] == paper_dict["title"] and p["date"] == paper_dict["date"] for p in cache[drug]):
        cache[drug].append(paper_dict)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
