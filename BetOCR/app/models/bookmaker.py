from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.bet import Bet

class Bookmaker(Base):
 __tablename__ = "bookmakers"
 id: Mapped[int] = mapped_column(Integer, primary_key=True)
 name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
 
 # Relationships
 bets: Mapped[list["Bet"]] = relationship("Bet", back_populates="bookmaker")