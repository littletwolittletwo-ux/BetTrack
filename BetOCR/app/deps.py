from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.config import settings
from app.models.user import User

def _noauth_user() -> User:
    u = User()
    u.id = 0
    u.username = "admin"
    u.role = "admin"
    u.is_active = True
    return u

def get_current_active_user() -> User:
    if settings.AUTH_DISABLED:
        return _noauth_user()
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

def get_current_admin() -> User:
    if settings.AUTH_DISABLED:
        return _noauth_user()
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")

CurrentUser = Annotated[User, Depends(get_current_active_user)]
AdminUser   = Annotated[User, Depends(get_current_admin)]

