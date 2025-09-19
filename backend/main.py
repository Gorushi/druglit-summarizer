import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # 1. CORS 미들웨어 임포트
from api.search import router as search_router
from services.db_manager import init_db

app = FastAPI(
    title="Drug Research Summarizer",
    description="약물 이름을 입력하면 PubMed 논문 검색 → 최신순 요약 결과 제공",
    version="1.0.0"
)

# 2. CORS 미들웨어 설정
# 프론트엔드 개발 서버 주소를 허용 목록에 추가
origins = [
    "http://localhost",
    "http://localhost:8000", # python -m http.server 기본 포트
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 앱 시작 시 DB 초기화
@app.on_event("startup")
def on_startup():
    init_db()

# 라우터 등록
app.include_router(search_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
