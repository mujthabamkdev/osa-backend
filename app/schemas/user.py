from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    role: str = "student"
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
class Config:
    from_attributes = True
