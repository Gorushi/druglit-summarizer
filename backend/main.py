import uvicorn
from fastapi import FastAPI
from api.search import router as search_router

app = FastAPI(
    title="Drug Research Summarizer",
    description="약물 이름을 입력하면 PubMed 논문 검색 → 최신순 요약 결과 제공",
    version="1.0.0"
)

# 라우터 등록
app.include_router(search_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

