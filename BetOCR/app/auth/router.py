from fastapi import APIRouter, HTTPException
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
        return LoginOut(access_token="dev-token")
    raise HTTPException(status_code=501, detail="Auth enabled; implement real login")
