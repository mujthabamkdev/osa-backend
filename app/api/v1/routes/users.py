from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.services.users import create_user, update_user, delete_user


router = APIRouter()


@router.get("/me", response_model=UserRead)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_admin(
    data: UserCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    try:
        return create_user(
            db,
            email=data.email,
            password=data.password,
            role=data.role,
            full_name=data.full_name,
            is_active=data.is_active,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists") from exc


@router.put("/{user_id}", response_model=UserRead)
def update_user_admin(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    try:
        return update_user(
            db,
            user_id,
            email=data.email,
            full_name=data.full_name,
            role=data.role,
            is_active=data.is_active,
            password=data.password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists") from exc


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    try:
        delete_user(db, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{user_id}/toggle-status", response_model=UserRead)
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user
