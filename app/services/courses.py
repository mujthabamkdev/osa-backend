from sqlalchemy.orm import Session
from app.models.course import Course

def create_course(db: Session, title: str, description: str, teacher_id: int) -> Course:
    c = Course(title=title, description=description, teacher_id=teacher_id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c
