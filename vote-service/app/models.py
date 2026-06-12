from datetime import datetime
from sqlalchemy import Integer, String, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Poll(Base):
    __tablename__ = "polls"
    id         : Mapped[int]      = mapped_column(Integer, primary_key=True)
    title      : Mapped[str]      = mapped_column(String(200), nullable=False)
    status     : Mapped[str]      = mapped_column(String(20), default="OPEN")
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PollBook(Base):
    """투표 후보 책 목록"""
    __tablename__ = "poll_books"
    id      : Mapped[int] = mapped_column(Integer, primary_key=True)
    poll_id : Mapped[int] = mapped_column(Integer, ForeignKey("polls.id"), nullable=False)
    book_id : Mapped[int] = mapped_column(Integer, nullable=False)

class VoteLog(Base):
    """중복 투표 방지 로그"""
    __tablename__ = "vote_logs"
    id      : Mapped[int] = mapped_column(Integer, primary_key=True)
    poll_id : Mapped[int] = mapped_column(Integer, nullable=False)
    user_id : Mapped[int] = mapped_column(Integer, nullable=False)
    book_id : Mapped[int] = mapped_column(Integer, nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("poll_id", "user_id", name="uq_one_vote_per_user"),
    )