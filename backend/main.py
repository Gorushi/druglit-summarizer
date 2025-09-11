from fastapi import FastAPI, Query
from pubmed_client import fetch_pubmed_articles
from summarizer import summarize_text

app = FastAPI()

@app.get("/search")
async def search_drug(drug: str = Query(..., description="Drug name to search for")):
    # 1. PubMed에서 논문 가져오기
    articles = fetch_pubmed_articles(drug, max_results=15)

    results = []
    for article in articles:
        title = article.get("title")
        abstract = article.get("abstract")
        
        # 초록이 있을 때만 요약 수행
        summary = summarize_text(abstract) if abstract else "No abstract available"

        results.append({
            "title": title,
            "abstract": abstract,
            "summary": summary,
            "pmid": article.get("pmid"),
            "link": f"https://pubmed.ncbi.nlm.nih.gov/{article.get('pmid')}/"
        })

    return {"drug": drug, "results": results}

