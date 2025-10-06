from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import LoginIn, TokenOut
from app.auth.hashing import verify_password
from app.auth.jwt_tools import create_access_token
from app.db.session import get_db
from app.crud.users import get_by_username

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
 user = get_by_username(db, payload.username)
 if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
     raise HTTPException(401, "Invalid credentials or user disabled")
 token = create_access_token(sub=str(user.id), role=user.role)
 return TokenOut(access_token=token, role=user.role)