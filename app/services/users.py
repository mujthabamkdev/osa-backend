from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password


def create_user(
    db: Session,
    email: str,
    password: str,
    role: str = "student",
    full_name: Optional[str] = None,
    is_active: bool = True,
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role,
        full_name=full_name,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session,
    user_id: int,
    *,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    password: Optional[str] = None,
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    if email is not None:
        user.email = email
    if full_name is not None:
        user.full_name = full_name
    if role is not None:
        user.role = role
    if is_active is not None:
        user.is_active = is_active
    if password:
        user.hashed_password = hash_password(password)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    db.delete(user)
    db.commit()
