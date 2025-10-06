import sys
import os

# Add the project root to Python path for imports to work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.db.session import SessionLocal
from app.auth.hashing import get_password_hash
from app.models import User
from app.db.init_data import init_core

if __name__ == "__main__":
 with SessionLocal() as db:
     init_core(db)
     if not db.query(User).filter_by(username=settings.DEFAULT_ADMIN_USERNAME).first():
         db.add(User(username=settings.DEFAULT_ADMIN_USERNAME,
                     password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                     role="admin", is_active=True))
     if not db.query(User).filter_by(username=settings.DEFAULT_EMPLOYEE_USERNAME).first():
         db.add(User(username=settings.DEFAULT_EMPLOYEE_USERNAME,
                     password_hash=get_password_hash(settings.DEFAULT_EMPLOYEE_PASSWORD),
                     role="employee", is_active=True))
     else:
         # Ensure employee has correct role/hash in case it existed without these
         emp = db.query(User).filter_by(username=settings.DEFAULT_EMPLOYEE_USERNAME).first()
         if emp:
             emp.role = "employee"
             emp.password_hash = get_password_hash(settings.DEFAULT_EMPLOYEE_PASSWORD)
             emp.is_active = True
             db.add(emp)
     db.commit()
     print("Seeded default admin and employee (dev only).")