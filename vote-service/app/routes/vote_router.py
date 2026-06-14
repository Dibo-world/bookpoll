from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from ..database import get_db, redis_client
from ..models import Poll, PollBook, VoteLog

router = APIRouter()


class PollCreate(BaseModel):
    title: str
    bookIds: List[int]


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
    poll = Poll(title=body.title)
    db.add(poll)
    db.flush()

    for book_id in body.bookIds:
        db.add(PollBook(poll_id=poll.id, book_id=book_id))

    db.commit()
    return ok({"pollId": poll.id, "title": poll.title}, status_code=201)


@router.get("/polls")
def list_polls(db: Session = Depends(get_db)):
    polls = db.query(Poll).filter(Poll.status == "OPEN").all()
    return ok([{"id": p.id, "title": p.title, "status": p.status} for p in polls])


@router.post("/polls/{poll_id}/cast")
def cast_vote(
    poll_id: int,
    body: CastVote,
    user_id: Optional[int] = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    if not user_id:
        return err("인증이 필요합니다", 401)

    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll or poll.status != "OPEN":
        return err("존재하지 않거나 종료된 투표입니다", 404)

    candidate = db.query(PollBook).filter(
        PollBook.poll_id == poll_id,
        PollBook.book_id == body.bookId
    ).first()
    if not candidate:
        return err("이 투표의 후보 도서가 아닙니다", 400)

    duplicate = db.query(VoteLog).filter_by(
        poll_id=poll_id,
        user_id=user_id
    ).first()
    if duplicate:
        return err("이미 투표하셨습니다", 409)

    redis_key = f"poll:{poll_id}:book:{body.bookId}"
    redis_client.incr(redis_key)

    log = VoteLog(poll_id=poll_id, user_id=user_id, book_id=body.bookId)
    db.add(log)
    db.commit()

    from app.rabbitmq import publish_vote_event
    publish_vote_event(poll_id=poll_id, user_id=user_id, book_id=body.bookId)

    return ok({"pollId": poll_id, "bookId": body.bookId}, message="투표 완료")


@router.get("/polls/{poll_id}/results")
def get_results(poll_id: int, db: Session = Depends(get_db)):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        return err("투표를 찾을 수 없습니다", 404)

    poll_books = db.query(PollBook).filter(PollBook.poll_id == poll_id).all()

    results = []
    for pb in poll_books:
        redis_key = f"poll:{poll_id}:book:{pb.book_id}"
        count = int(redis_client.get(redis_key) or 0)
        results.append({
            "bookId": pb.book_id,
            "votes": count
        })

    results.sort(key=lambda x: x["votes"], reverse=True)
    return ok(results)


@router.get("/polls/my-votes")
def get_my_votes(
    user_id: Optional[int] = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    if not user_id:
        return err("인증 필요", 401)

    rows = (
        db.query(VoteLog)
        .filter(VoteLog.user_id == user_id)
        .order_by(VoteLog.created_at.desc())
        .all()
    )

    data = [
        {
            "pollId": row.poll_id,
            "bookId": row.book_id,
            "votedAt": row.created_at.isoformat()
        }
        for row in rows
    ]
    return ok(data=data)