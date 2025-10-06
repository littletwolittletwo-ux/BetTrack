from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt_tools import decode_token
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.user import User

bearer = HTTPBearer(auto_error=True)

def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
 try:
     payload = decode_token(creds.credentials)
     uid = int(payload["sub"]); role = payload.get("role")
 except Exception:
     raise HTTPException(401, "Invalid token")
 user = db.get(User, uid)
 if not user or not user.is_active:
     raise HTTPException(401, "User disabled")
 user._role = role
 return user

def require_admin(user: User = Depends(current_user)) -> User:
 if getattr(user, "_role", None) != "admin":
     raise HTTPException(403, "Admin only")
 return user