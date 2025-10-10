from sqlalchemy import (
 Integer, String, Numeric, TIMESTAMP, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.bookmaker import Bookmaker

class Bet(Base):
 __tablename__ = "bets"
 id: Mapped[int] = mapped_column(primary_key=True)
 set_id: Mapped[int] = mapped_column(ForeignKey("bet_sets.id"), nullable=False)
 bookmaker_id: Mapped[int] = mapped_column(ForeignKey("bookmakers.id"), nullable=False)
 uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
 uploaded_at: Mapped[datetime] = mapped_column(TIMESTAMP)
 image_path: Mapped[str] = mapped_column(Text, nullable=False)

 event_text: Mapped[str | None]
 bet_type: Mapped[str | None]
 odds_numeric: Mapped[float | None]
 stake_manual: Mapped[float]
 potential_return: Mapped[float | None]
 cashout_amount: Mapped[float | None]
 commission_rate: Mapped[float | None]
 result_status: Mapped[str | None]
 settled_at: Mapped[str | None]
 profit: Mapped[float]

 raw_ocr_json: Mapped[dict | None] = mapped_column(JSONB)
 parse_version: Mapped[int]
 last_edited_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
 last_edited_at: Mapped[datetime | None] = mapped_column(TIMESTAMP)
 
 # Relationships
 bookmaker: Mapped["Bookmaker"] = relationship("Bookmaker", back_populates="bets")
