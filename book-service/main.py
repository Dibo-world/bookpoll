# book-service/main.py
from fastapi import FastAPI
from app.database import Base, engine
from app.routes.book_router import router
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5501",
    "http://127.0.0.1:5501",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app = FastAPI(title="Book Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Instrumentator().instrument(app).expose(app)
app.include_router(router, prefix="/api/v1/books")

@app.get("/health")
def health():
    return {"status": "ok", "service": "book-service"}