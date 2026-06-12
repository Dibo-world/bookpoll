from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class User(Base):
    __tablename__ = "users"

    id         : Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    email      : Mapped[str]      = mapped_column(String(120), unique=True, nullable=False)
    password   : Mapped[str]      = mapped_column(String(255), nullable=False)
    username   : Mapped[str]      = mapped_column(String(80), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)