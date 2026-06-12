from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models import Book

router = APIRouter()

# ── 스키마 ─────────────────────────────────────────────
class BookCreate(BaseModel):
    title: str
    author: str
    description: Optional[str] = ""

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None

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

def get_user_id(x_user_id: Optional[str] = Header(None)) -> Optional[int]:
    """
    3-2 단계: 테스트용으로 X-User-Id 헤더 직접 사용
    3-3 단계: auth-service /verify 호출로 교체 예정
    """
    return int(x_user_id) if x_user_id else None

# ── 책 목록 조회 ──────────────────────────────────────────
@router.get("")
def list_books(db: Session = Depends(get_db)):
    books = db.query(Book).order_by(Book.created_at.desc()).all()
    data = [
        {"id": b.id, "title": b.title, "author": b.author,
         "description": b.description, "userId": b.user_id}
        for b in books
    ]
    return ok(data)

# ── 책 상세 조회 ──────────────────────────────────────────
@router.get("/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return err("책을 찾을 수 없습니다", 404)
    return ok({"id": book.id, "title": book.title,
                "author": book.author, "description": book.description})

# ── 책 등록 ───────────────────────────────────────────────
@router.post("")
def create_book(
    body: BookCreate,
    user_id: Optional[int] = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    if not user_id:
        return err("인증이 필요합니다", 401)

    book = Book(title=body.title, author=body.author,
                description=body.description, user_id=user_id)
    db.add(book)
    db.commit()
    db.refresh(book)
    return ok({"id": book.id, "title": book.title, "author": book.author}, 201)

# ── 책 수정 ───────────────────────────────────────────────
@router.put("/{book_id}")
def update_book(
    book_id: int,
    body: BookUpdate,
    user_id: Optional[int] = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return err("책을 찾을 수 없습니다", 404)
    if book.user_id != user_id:
        return err("본인이 등록한 책만 수정할 수 있습니다", 403)

    if body.title:       book.title       = body.title
    if body.author:      book.author      = body.author
    if body.description: book.description = body.description
    db.commit()
    return ok({"id": book.id, "title": book.title})

# ── 책 삭제 ───────────────────────────────────────────────
@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    user_id: Optional[int] = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return err("책을 찾을 수 없습니다", 404)
    if book.user_id != user_id:
        return err("본인이 등록한 책만 삭제할 수 있습니다", 403)

    db.delete(book)
    db.commit()
    return ok(message="삭제 완료")