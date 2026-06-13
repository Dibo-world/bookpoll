from fastapi import FastAPI
from app.database import Base, engine
from app.routes.vote_router import router
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vote Service", version="1.0.0", root_path="/votes")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)   
Instrumentator().instrument(app).expose(app)
app.include_router(router, prefix="/api/v1/votes")

@app.get("/health")
def health():
    return {"status": "ok", "service": "vote-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)