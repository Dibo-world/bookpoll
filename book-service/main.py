from fastapi import FastAPI
from app.database import Base, engine
from app.routes.book_router import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Service", version="1.0.0")
app.include_router(router, prefix="/api/v1/books")

@app.get("/health")
def health():
    return {"status": "ok", "service": "book-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)