from app.config import settings
from app.db.session import SessionLocal
from app.auth.hashing import get_password_hash
from app.models.user import User

if __name__ == "__main__":
 with SessionLocal() as db:
     if not db.query(User).filter_by(username=settings.DEFAULT_ADMIN_USERNAME).first():
         db.add(User(username=settings.DEFAULT_ADMIN_USERNAME,
                     password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                     role="admin", is_active=True))
     db.commit()
     print("Admin ensured.")