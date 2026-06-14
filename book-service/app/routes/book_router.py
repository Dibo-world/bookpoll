# app/routes/book_router.py
import os
import shutil
import uuid
from fastapi import APIRouter, Depends, Header, Form, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import Book

router = APIRouter()

# 이미지가 저장될 실제 디렉토리 설정 (서버 실행 시 폴더가 없으면 자동 생성)
UPLOAD_DIR = "static/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── 공통 응답 함수 ──────────────────────────────────────────
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
    return int(x_user_id) if x_user_id else None

# ── 1. 책 목록 조회 ──────────────────────────────────────────
@router.get("")
def list_books(db: Session = Depends(get_db)):
    books = db.query(Book).order_by(Book.created_at.desc()).all()
    data = [
        {
            "id": b.id, 
            "title": b.title, 
            "author": b.author,
            "description": b.description, 
            "userId": b.user_id,
            "imageUrl": b.image_url  
        }
        for b in books
    ]
    return ok(data)

# ── 2. 책 등록 (이미지 업로드 포함) ──────────────────────────────────
@router.post("")
async def create_book(
    title: str = Form(...),
    author: str = Form(...),
    description: Optional[str] = Form(""),
    image: Optional[UploadFile] = File(None),
    user_id: Optional[int] = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    if not user_id:
        return err("인증이 필요합니다", 401)

    image_url = None
    # 사용자가 이미지를 첨부한 경우
    if image and image.filename:
        # 파일명 중복을 피하기 위해 난수(UUID)로 파일명 생성
        file_ext = image.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        # 파일 물리적 저장
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # DB에 기록될 URL (프론트에서 이 주소로 접근)
        image_url = f"/static/images/{file_name}"

    book = Book(
        title=title, 
        author=author,
        description=description, 
        image_url=image_url,
        user_id=user_id
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    
    return ok({
        "id": book.id, 
        "title": book.title, 
        "author": book.author,
        "imageUrl": book.image_url
    }, "등록 성공", 201)

# ── 3. 책 수정 (이미지 수정 포함) ──────────────────────────────────
@router.put("/{book_id}")
async def update_book(
    book_id: int,
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    user_id: Optional[int] = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return err("책을 찾을 수 없습니다", 404)
    if book.user_id != user_id:
        return err("본인이 등록한 책만 수정할 수 있습니다", 403)

    if title is not None:
        book.title = title
    if author is not None:
        book.author = author
    if description is not None:
        book.description = description
    
    # 새로운 이미지가 업로드된 경우 기존 이미지 교체
    if image and image.filename:
        file_ext = image.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        book.image_url = f"/static/images/{file_name}"

    db.commit()
    return ok({
        "id": book.id, 
        "title": book.title, 
        "imageUrl": book.image_url
    }, "수정 완료")

# ── 4. 책 삭제 ───────────────────────────────────────────────
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
    return ok(None, "삭제 완료")