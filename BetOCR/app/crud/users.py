from sqlalchemy.orm import Session
from app.models.user import User

def get_by_username(db: Session, username: str) -> User | None:
 return db.query(User).filter(User.username == username).first()

def create(db: Session, username: str, password_hash: str, role: str) -> User:
 u = User(username=username, password_hash=password_hash, role=role, is_active=True)
 db.add(u); db.commit(); db.refresh(u); return u

def list_users(db: Session, role: str | None=None, active: bool | None=None):
 q = db.query(User)
 if role: q = q.filter(User.role == role)
 if active is not None: q = q.filter(User.is_active == active)
 return q.order_by(User.id).all()
