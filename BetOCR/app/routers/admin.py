from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import AdminUser, CurrentUser
from app.db.session import get_db
from app.schemas.users import UserCreate, UserUpdate, UserStatusPatch, PasswordReset, UserOut
from app.schemas.sets import SetCreate, SetUpdate, SetStatusPatch, SetOut
from app.auth.hashing import get_password_hash
from app.models.user import User
from app.models.bet_set import BetSet
from app.crud.users import list_users
from app.crud.sets import list_sets, create as create_set, rename as rename_set, set_status as set_set_status
from app.services.cleanup import cleanup_old_images, cleanup_orphaned_images

router = APIRouter(prefix="/admin", tags=["admin"])

# Users
@router.post("/users", response_model=UserOut)
def create_user(body: UserCreate, db: Session = Depends(get_db), admin = Depends(AdminUser)):
 if db.query(User).filter_by(username=body.username).first():
     raise HTTPException(400, "Username exists")
 u = User(username=body.username, password_hash=get_password_hash(body.password), role=body.role, is_active=True)
 db.add(u); db.commit(); db.refresh(u); return u

@router.get("/users", response_model=list[UserOut])
def get_users(role: str | None=None, active: bool | None=None, db: Session = Depends(get_db), admin = Depends(AdminUser)):
 return list_users(db, role=role, active=active)

@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db), admin = Depends(AdminUser)):
 u = db.get(User, user_id)
 if not u: raise HTTPException(404, "Not found")
 if body.username:
     if db.query(User).filter(User.username==body.username, User.id!=user_id).first():
         raise HTTPException(400, "Username taken")
     u.username = body.username
 if body.role: u.role = body.role
 db.add(u); db.commit(); db.refresh(u); return u

@router.patch("/users/{user_id}/status", response_model=UserOut)
def patch_user_status(user_id: int, body: UserStatusPatch, db: Session = Depends(get_db), admin = Depends(AdminUser)):
 u = db.get(User, user_id)
 if not u: raise HTTPException(404, "Not found")
 u.is_active = body.is_active
 db.add(u); db.commit(); db.refresh(u); return u

@router.post("/users/{user_id}/password")
def reset_password(user_id: int, body: PasswordReset, db: Session = Depends(get_db), admin = Depends(AdminUser)):
 u = db.get(User, user_id)
 if not u: raise HTTPException(404, "Not found")
 u.password_hash = get_password_hash(body.password)
 db.add(u); db.commit(); return {"ok": True}

# Sets
@router.post("/sets", response_model=SetOut)
def create_set_route(body: SetCreate, db: Session = Depends(get_db), admin = Depends(AdminUser)):
 if db.query(BetSet).filter_by(name=body.name).first():
     raise HTTPException(400, "Set name exists")
 return create_set(db, body.name)

@router.get("/sets", response_model=list[SetOut])
def list_sets_route(active: bool | None=None, db: Session = Depends(get_db), user = Depends(CurrentUser)):
 # Only allow employees to view active sets, admins can see all
 if getattr(user, "_role", None) == "employee" and active is not False:
     active = True  # Force employees to only see active sets
 return list_sets(db, active=active)

@router.put("/sets/{set_id}", response_model=SetOut)
def rename_set_route(set_id: int, body: SetUpdate, db: Session = Depends(get_db), admin = Depends(AdminUser)):
 s = rename_set(db, set_id, body.name)
 if not s: raise HTTPException(404, "Not found")
 return s

@router.patch("/sets/{set_id}/status", response_model=SetOut)
def patch_set_status_route(set_id: int, body: SetStatusPatch, db: Session = Depends(get_db), admin = Depends(AdminUser)):
 s = set_set_status(db, set_id, body.is_active)
 if not s: raise HTTPException(404, "Not found")
 return s

# Cleanup endpoints
@router.post("/cleanup/images")
def cleanup_images_endpoint(retention_days: int = 7, admin = Depends(AdminUser)):
    """Clean up image files older than retention_days (default 7 days)"""
    result = cleanup_old_images(retention_days)
    return {"message": "Image cleanup completed", "result": result}

@router.post("/cleanup/orphaned")
def cleanup_orphaned_endpoint(admin = Depends(AdminUser)):
    """Clean up image files that have no corresponding database records"""
    result = cleanup_orphaned_images()
    return {"message": "Orphaned image cleanup completed", "result": result}
