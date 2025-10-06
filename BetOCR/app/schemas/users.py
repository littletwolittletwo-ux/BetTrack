from pydantic import BaseModel, constr
from typing import Optional, Literal

class UserOut(BaseModel):
 id: int
 username: str
 role: Literal["admin","employee"]
 is_active: bool
 class Config: from_attributes = True

class UserCreate(BaseModel):
 username: constr(min_length=3, max_length=50)
 password: constr(min_length=4)
 role: Literal["admin","employee"]

class UserUpdate(BaseModel):
 username: Optional[constr(min_length=3, max_length=50)] = None
 role: Optional[Literal["admin","employee"]] = None

class UserStatusPatch(BaseModel):
 is_active: bool

class PasswordReset(BaseModel):
 password: constr(min_length=6)