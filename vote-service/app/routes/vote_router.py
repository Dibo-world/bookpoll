from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel  # 🌟 복잡한 벨리데이터 임포트 전부 제거!
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db, redis_client
from ..models import Book, Poll, PollBook, VoteLog

router = APIRouter()


# 🌟 Pydantic 버전 충돌을 피하기 위해 deadline을 안전하게 일반 문자열(str)로 받습니다.
class PollCreate(BaseModel):
    title: str
    bookIds: List[int]
    deadline: Optional[str] = None  


class CastVote(BaseModel):
    bookId: int


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


@router.post("/polls")
def create_poll(body: PollCreate, db: Session = Depends(get_db)):
    if not body.title.strip():
        return err("투표 제목은 비어 있을 수 없습니다.", 400)

    unique_book_ids = list(dict.fromkeys(body.bookIds))
    if len(unique_book_ids) < 2:
        return err("후보 도서는 최소 2권 이상이어야 합니다.", 400)

    books = db.query(Book).filter(Book.id.in_(unique_book_ids)).all()
    if len(books) != len(unique_book_ids):
        return err("존재하지 않는 도서가 포함되어 있습니다.", 400)

    # 🌟 [수동 검증 체계] 들어온 문자열을 함수 내부에서 안전하게 변환합니다.
    poll_deadline = None
    if body.deadline and body.deadline.strip():  # 빈 문자열("")이 아니면 변환 시도
        try:
            # 프론트엔드의 ISO 포맷("Z")을 파싱 가능하도록 보정 처리
            iso_str = body.deadline.replace("Z", "+00:00")
            poll_deadline = datetime.fromisoformat(iso_str)
        except Exception:
            return err("올바르지 않은 날짜 형식입니다.", 400)

    poll = Poll(
        title=body.title.strip(), 
        status="OPEN",
        deadline=poll_deadline  # 변환된 datetime 객체 또는 None이 안전하게 들어감
    )
    db.add(poll)
    db.flush()

    for book_id in unique_book_ids:
        db.add(PollBook(poll_id=poll.id, book_id=book_id))

    db.commit()

    return ok(
        {
            "pollId": poll.id,
            "title": poll.title,
            "bookIds": unique_book_ids,
            "deadline": poll.deadline.isoformat() if poll.deadline else None
        },
        message="투표 생성 완료",
        status_code=201
    )


@router.get("/polls")
def list_polls(db: Session = Depends(get_db)):
    polls = db.query(Poll).order_by(Poll.created_at.desc()).all()

    data = []
    for p in polls:
        poll_book_ids = (
            db.query(PollBook.book_id)
            .filter(PollBook.poll_id == p.id)
            .all()
        )
        book_ids = [row[0] for row in poll_book_ids]

        data.append({
            "id": p.id,
            "title": p.title,
            "status": p.status,
            "createdAt": p.created_at.isoformat() if p.created_at else None,
            "deadline": p.deadline.isoformat() if p.deadline else None,  # 목록에 정상 포함
            "bookIds": book_ids
        })

    return ok(data)


@router.get("/polls/my-votes")
def get_my_votes(
    user_id: Optional[int] = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    if not user_id:
        return err("인증 필요", 401)

    rows = (
        db.query(VoteLog, Poll, Book)
        .join(Poll, VoteLog.poll_id == Poll.id)
        .join(Book, VoteLog.book_id == Book.id)
        .filter(VoteLog.user_id == user_id)
        .order_by(VoteLog.created_at.desc())
        .all()
    )

    data = [
        {
            "pollId": vote_log.poll_id,
            "pollTitle": poll.title,
            "votedBookId": book.id,
            "votedBookTitle": book.title,
            "votedAt": vote_log.created_at.isoformat() if vote_log.created_at else None
        }
        for vote_log, poll, book in rows
    ]

    return ok(data)


@router.get("/polls/{poll_id}")
def get_poll_detail(poll_id: int, db: Session = Depends(get_db)):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        return err("투표를 찾을 수 없습니다.", 404)

    books = (
        db.query(Book)
        .join(PollBook, PollBook.book_id == Book.id)
        .filter(PollBook.poll_id == poll_id)
        .order_by(Book.id.asc())
        .all()
    )

    data = {
        "id": poll.id,
        "title": poll.title,
        "status": poll.status,
        "createdAt": poll.created_at.isoformat() if poll.created_at else None,
        "deadline": poll.deadline.isoformat() if poll.deadline else None,
        "books": [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "description": b.description,
                "imageUrl": None
            }
            for b in books
        ]
    }

    return ok(data)


@router.get("/polls/{poll_id}/results")
def get_results(poll_id: int, db: Session = Depends(get_db)):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        return err("투표를 찾을 수 없습니다.", 404)

    rows = (
        db.query(
            PollBook.book_id.label("book_id"),
            func.count(VoteLog.id).label("votes")
        )
        .outerjoin(
            VoteLog,
            (VoteLog.poll_id == PollBook.poll_id) &
            (VoteLog.book_id == PollBook.book_id)
        )
        .filter(PollBook.poll_id == poll_id)
        .group_by(PollBook.book_id)
        .order_by(func.count(VoteLog.id).desc(), PollBook.book_id.asc())
        .all()
    )

    data = [
        {
            "bookId": row.book_id,
            "votes": int(row.votes or 0)
        }
        for row in rows
    ]

    return ok(data)


@router.post("/polls/{poll_id}/cast")
def cast_vote(
    poll_id: int,
    body: CastVote,
    user_id: Optional[int] = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    if not user_id:
        return err("인증이 필요합니다.", 401)

    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll or poll.status != "OPEN":
        return err("존재하지 않거나 종료된 투표입니다.", 404)

    candidate = (
        db.query(PollBook)
        .filter(
            PollBook.poll_id == poll_id,
            PollBook.book_id == body.bookId
        )
        .first()
    )
    if not candidate:
        return err("이 투표의 후보 도서가 아닙니다.", 400)

    duplicate = (
        db.query(VoteLog)
        .filter(
            VoteLog.poll_id == poll_id,
            VoteLog.user_id == user_id
        )
        .first()
    )
    if duplicate:
        return err("이미 투표하셨습니다.", 409)

    try:
        log = VoteLog(
            poll_id=poll_id,
            user_id=user_id,
            book_id=body.bookId
        )
        db.add(log)
        db.commit()
    except IntegrityError:
        db.rollback()
        return err("이미 투표하셨습니다.", 409)

    try:
        redis_key = f"poll:{poll_id}:book:{body.bookId}"
        redis_client.incr(redis_key)
    except Exception:
        pass

    try:
        from app.rabbitmq import publish_vote_event
        publish_vote_event(poll_id=poll_id, user_id=user_id, book_id=body.bookId)
    except Exception:
        pass

    return ok(
        {"pollId": poll_id, "bookId": body.bookId},
        message="투표 완료"
    )