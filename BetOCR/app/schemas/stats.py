from pydantic import BaseModel

class SetStatsOut(BaseModel):
 set_id: int
 set_name: str
 total_bets: int
 wins: int
 net_profit: float
 avg_roi: float | None
