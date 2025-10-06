from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class BetSet(Base):
 __tablename__ = "bet_sets"
 id: Mapped[int] = mapped_column(Integer, primary_key=True)
 name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
 is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)