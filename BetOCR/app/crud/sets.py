from sqlalchemy.orm import Session
from app.models.bet_set import BetSet

def create(db: Session, name: str) -> BetSet:
 s = BetSet(name=name, is_active=True)
 db.add(s); db.commit(); db.refresh(s); return s

def list_sets(db: Session, active: bool | None=None):
 q = db.query(BetSet)
 if active is not None: q = q.filter(BetSet.is_active == active)
 return q.order_by(BetSet.name).all()

def rename(db: Session, set_id: int, name: str) -> BetSet | None:
 s = db.get(BetSet, set_id)
 if not s: return None
 s.name = name; db.add(s); db.commit(); db.refresh(s); return s

def set_status(db: Session, set_id: int, is_active: bool) -> BetSet | None:
 s = db.get(BetSet, set_id)
 if not s: return None
 s.is_active = is_active; db.add(s); db.commit(); db.refresh(s); return s