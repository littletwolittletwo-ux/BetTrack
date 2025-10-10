from datetime import datetime, timedelta
import jwt
from app.config import settings

def create_access_token(sub: str, role: str, expires_minutes: int | None=None) -> str:
 to_encode = {"sub": sub, "role": role, "iat": int(datetime.utcnow().timestamp())}
 expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
 to_encode.update({"exp": expire})
 return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str):
 return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
