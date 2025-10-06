from pydantic import BaseModel
from typing import Optional

class BetUploadIn(BaseModel):
 set_id: int
 bookmaker_name: str
 stake_manual: float

class BetUpdate(BaseModel):
    stake_manual: Optional[float] = None
    odds_numeric: Optional[float] = None
    potential_return: Optional[float] = None
    result_status: Optional[str] = None
    bet_type: Optional[str] = None

class BetOut(BaseModel):
 id: int
 set_id: int
 bookmaker_id: int
 stake_manual: float
 odds_numeric: Optional[float] = None
 result_status: Optional[str] = None
 profit: float
 image_path: Optional[str] = None
 event_text: Optional[str] = None  # OCR text
 bet_type: Optional[str] = None
 potential_return: Optional[float] = None
 class Config: from_attributes = True