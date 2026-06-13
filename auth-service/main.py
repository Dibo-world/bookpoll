from fastapi import FastAPI
from app.database import Base, engine
from app.routes.auth_router import router
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware  

# 앱 시작 시 DB 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service", version="1.0.0", root_path="/auth")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Instrumentator().instrument(app).expose(app)
app.include_router(router, prefix="/api/v1/auth")

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)