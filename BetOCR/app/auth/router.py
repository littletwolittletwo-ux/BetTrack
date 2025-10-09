from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginIn(BaseModel):
    username: str
    password: str

class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=LoginOut)
def login(_: LoginIn):
    if settings.AUTH_DISABLED:
        # Always succeed with a fake token for the frontend
        return LoginOut(access_token="dev-token")
    # If you ever re-enable auth, implement the real login here:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Auth enabled; implement real login")
