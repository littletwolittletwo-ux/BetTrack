from sqlalchemy.orm import Session
from app.models import BetSet, Bookmaker

SET_NAMES = ["s","c","a","o","d","k"]
BOOKMAKERS = ["Ladbrokes","PointsBet","Sportsbet","TAB","bet365","Betfair"]

def init_core(db: Session):
 for n in SET_NAMES:
     if not db.query(BetSet).filter_by(name=n).first():
         db.add(BetSet(name=n, is_active=True))
 for n in BOOKMAKERS:
     if not db.query(Bookmaker).filter_by(name=n).first():
         db.add(Bookmaker(name=n))
 db.commit()