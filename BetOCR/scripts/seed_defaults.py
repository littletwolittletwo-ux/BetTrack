# scripts/seed_defaults.py
from app.config import settings
from app.db.session import SessionLocal
from app.auth.hashing import get_password_hash
from app.models.user import User
from app.db.init_data import init_core

if __name__ == "__main__":
    with SessionLocal() as db:
        # create core reference data if your project uses it
        try:
            init_core(db)
        except Exception:
            # safe to continue even if not present
            pass

        # ensure admin
        admin = db.query(User).filter_by(username=settings.DEFAULT_ADMIN_USERNAME).first()
        if not admin:
            db.add(User(
                username=settings.DEFAULT_ADMIN_USERNAME,
                password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                role="admin",
                is_active=True,
            ))
        else:
            admin.role = "admin"
            admin.password_hash = get_password_hash(settings.DEFAULT_ADMIN_PASSWORD)
            admin.is_active = True
            db.add(admin)

        # ensure employee
        emp = db.query(User).filter_by(username=settings.DEFAULT_EMPLOYEE_USERNAME).first()
        if not emp:
            db.add(User(
                username=settings.DEFAULT_EMPLOYEE_USERNAME,
                password_hash=get_password_hash(settings.DEFAULT_EMPLOYEE_PASSWORD),
                role="employee",
                is_active=True,
            ))
        else:
            emp.role = "employee"
            emp.password_hash = get_password_hash(settings.DEFAULT_EMPLOYEE_PASSWORD)
            emp.is_active = True
            db.add(emp)

        db.commit()
        print("Seeded default admin and employee.")
