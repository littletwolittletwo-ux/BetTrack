from sqlalchemy import String, Boolean, Integer, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class User(Base):
 __tablename__ = "users"
 id: Mapped[int] = mapped_column(Integer, primary_key=True)
 username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
 password_hash: Mapped[str] = mapped_column(nullable=False)
 role: Mapped[str] = mapped_column(String(20), nullable=False)
 is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
 created_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=text("NOW()"))
