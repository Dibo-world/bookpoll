from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Book(Base):
    __tablename__ = "books"

    id          : Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    title       : Mapped[str]      = mapped_column(String(200), nullable=False)
    author      : Mapped[str]      = mapped_column(String(100), nullable=False)
    description : Mapped[str]      = mapped_column(Text, default="")
    user_id     : Mapped[int]      = mapped_column(Integer, nullable=False)
    created_at  : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at  : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                   onupdate=datetime.utcnow)