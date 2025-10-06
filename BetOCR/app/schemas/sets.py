from pydantic import BaseModel, constr

class SetOut(BaseModel):
 id: int
 name: str
 is_active: bool
 class Config: from_attributes = True

class SetCreate(BaseModel):
 name: constr(min_length=1, max_length=100)

class SetUpdate(BaseModel):
 name: constr(min_length=1, max_length=100)

class SetStatusPatch(BaseModel):
 is_active: bool