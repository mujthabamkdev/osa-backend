from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import (verify_password, create_access_token,
                               get_password_hash)
from app.models.user import User

router = APIRouter()


class LoginDTO(BaseModel):
    email: EmailStr
    password: str


class RegisterDTO(BaseModel):
    email: EmailStr
    password: str
    fullName: str
    role: Optional[str] = "student"


@router.post("/login", status_code=200)
def login(dto: LoginDTO, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == dto.email).first()
    if not user or not verify_password(dto.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")

    token = create_access_token({"sub": user.email,
                                 "id": user.id,
                                 "role": user.role})

    return {"access_token": token,
            "token_type": "bearer",
            "user": {"id": user.id, "email": user.email,
                     "fullName": user.full_name, "role": user.role}}


@router.post("/register", status_code=201)
async def register(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    dto = RegisterDTO(**body)

    if db.query(User).filter(User.email == dto.email).first():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"detail": "Email already registered"})

    new_user = User(email=dto.email,
                    hashed_password=get_password_hash(dto.password),
                    full_name=dto.fullName,
                    role=dto.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.email,
                                 "id": new_user.id,
                                 "role": new_user.role})

    return {"token": token,
            "user": {"id": new_user.id, "email": new_user.email,
                     "fullName": new_user.full_name, "role": new_user.role}}
