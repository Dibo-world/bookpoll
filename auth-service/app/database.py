from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# FastAPI Dependency — 라우터에서 DB 세션 주입용
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()