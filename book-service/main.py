# book-service/main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles 
from app.database import Base, engine
from app.routes.book_router import router
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

# 이미지를 저장할 폴더가 없으면 미리 생성
os.makedirs("static/images", exist_ok=True)  # 👈 추가

ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5501",
    "http://127.0.0.1:5501",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003",
    "http://localhost:8004",
]

app = FastAPI(title="Book Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# /static 경로로 들어오는 요청은 static 폴더 안의 파일들로 응답하겠다는 통로 설정
app.mount("/static", StaticFiles(directory="static"), name="static")  # 👈 추가

Instrumentator().instrument(app).expose(app)
app.include_router(router, prefix="/api/v1/books")

@app.get("/health")
def health():
    return {"status": "ok", "service": "book-service"}