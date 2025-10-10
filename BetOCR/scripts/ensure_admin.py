# scripts/ensure_admin.py
from app.config import settings
from app.db.session import SessionLocal
from app.auth.hashing import get_password_hash
from app.models.user import User

if __name__ == "__main__":
    with SessionLocal() as db:
        # create admin if missing
        admin = db.query(User).filter_by(username=settings.DEFAULT_ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=settings.DEFAULT_ADMIN_USERNAME,
                password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            print("Created admin.")
        else:
            # ensure correct role/hash/active if it already exists
            admin.role = "admin"
            admin.password_hash = get_password_hash(settings.DEFAULT_ADMIN_PASSWORD)
            admin.is_active = True
            db.add(admin)
            print("Updated existing admin.")
        db.commit()
        print("Admin ensured.")
