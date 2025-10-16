from app.core.security import get_password_hash   
from typing import List
from app.core.db import get_db
from app.schemas.user import UserRead, UserCreate
from app.models.user import User
from app.api.v1.deps import get_current_user, require_role
from app.services.users import create_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.deps import get_current_user, require_role
from app.models.user import User

router = APIRouter()

@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "fullName": current_user.full_name,
        "role": current_user.role
    }

@router.get("/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    return db.query(User).order_by(User.id.asc()).all()

@router.post("/", response_model=UserRead, status_code=201)
def create_user_admin(data: UserCreate, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    return create_user(db, email=data.email, password=data.password, role=data.role)
