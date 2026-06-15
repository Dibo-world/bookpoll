from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import bcrypt, jwt, os

from ..database import get_db
from ..models import User
from ..config import settings

router = APIRouter()

# ── Pydantic 요청/응답 스키마 ────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str

class LoginRequest(BaseModel):
    email: str
    password: str

class VerifyRequest(BaseModel):
    token: str

def ok(data=None, message="ok", status_code=200):
    return JSONResponse(
        status_code=status_code,
        content={"success": True, "data": data, "message": message}
    )

def err(message="error", status_code=400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "data": None, "message": message}
    )

def create_token(user: User) -> str:
    payload = {
        "userId": user.id,
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    }
    secret_key = settings.JWT_SECRET or "fallback_secret_key_for_bookpoll_2026"
    return jwt.encode(payload, secret_key, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

# ── 회원가입 ──────────────────────────────────────────────
@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        return err("이미 존재하는 이메일", 409)

    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    user = User(email=body.email, password=hashed, username=body.username)
    db.add(user)
    db.commit()
    db.refresh(user)

    return ok({"userId": user.id, "username": user.username}, status_code=201)

# ── 로그인 ────────────────────────────────────────────────
@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not bcrypt.checkpw(body.password.encode(), user.password.encode()):
        return err("이메일 또는 비밀번호 오류", 401)

    token = create_token(user)
    return ok({"token": token, "userId": user.id, "username": user.username})

# ── 내 정보 조회 ──────────────────────────────────────────
@router.get("/me")
def me(authorization: str = None, db: Session = Depends(get_db)):
    # Header: Authorization: Bearer {token}
    from fastapi import Request, Header
    return {"hint": "/me는 아래 verify 로직 참고해서 완성하기"}

# ── JWT 검증 (내부 서비스 전용) ───────────────────────────
@router.post("/verify")
def verify(body: VerifyRequest):
    try:
        payload = decode_token(body.token)
        return ok({"userId": payload["userId"], "username": payload["username"]})
    except jwt.ExpiredSignatureError:
        return err("토큰이 만료됐습니다", 401)
    except Exception:
        return err("유효하지 않은 토큰", 401)