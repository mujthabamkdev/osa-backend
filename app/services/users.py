from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password

def create_user(db: Session, email: str, password: str, role: str = "student") -> User:
    u = User(email=email, hashed_password=hash_password(password), role=role, is_active=True)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
