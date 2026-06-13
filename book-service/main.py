# book-service/main.py
from fastapi import FastAPI
from app.database import Base, engine
from app.routes.book_router import router
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Service", version="1.0.0", root_path="/books")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)
Instrumentator().instrument(app).expose(app)
app.include_router(router, prefix="/api/v1/books")

@app.get("/health")
def health():
    return {"status": "ok", "service": "book-service"}