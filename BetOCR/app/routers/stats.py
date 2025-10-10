from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.deps import CurrentUser
from app.crud.bets import set_stats
from app.schemas.stats import SetStatsOut

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/sets", response_model=list[SetStatsOut])
def sets_stats(hours: int = 72, db: Session = Depends(get_db), user = Depends(CurrentUser)):
 return [SetStatsOut(**dict(r._mapping)) for r in set_stats(db, hours=hours)]
