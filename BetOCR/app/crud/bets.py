from sqlalchemy.orm import Session
from sqlalchemy import func, case, text
from app.models.bet import Bet
from app.models.bookmaker import Bookmaker

def get_or_create_bookmaker(db: Session, name: str) -> int:
 name = name.strip()
 bk = db.query(Bookmaker).filter_by(name=name).first()
 if not bk:
     bk = Bookmaker(name=name); db.add(bk); db.commit(); db.refresh(bk)
 return bk.id

def create_bet(db: Session, **kwargs) -> Bet:
 b = Bet(**kwargs)
 db.add(b); db.commit(); db.refresh(b); return b

def recent_bets(db: Session, hours: int = 72, set_id: int | None=None):
 q = db.query(Bet).filter(Bet.uploaded_at >= func.now() - text(f"INTERVAL '{hours} HOURS'"))
 if set_id: q = q.filter(Bet.set_id == set_id)
 return q.order_by(Bet.uploaded_at.desc()).all()

def set_stats(db: Session, hours: int = 72):
 b = Bet
 from app.models.bet_set import BetSet
 s = BetSet
 q = db.query(
     b.set_id.label("set_id"),
     s.name.label("set_name"),
     func.count().label("total_bets"),
     func.sum(case((b.result_status=='won', 1), else_=0)).label("wins"),
     func.coalesce(func.sum(b.profit), 0).label("net_profit"),
     func.avg(case((b.stake_manual>0, b.profit/b.stake_manual), else_=None)).label("avg_roi")
 ).join(s, b.set_id == s.id).filter(b.uploaded_at >= func.now() - text(f"INTERVAL '{hours} HOURS'")).group_by(b.set_id, s.name)
 return q.all()
