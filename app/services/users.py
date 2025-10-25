from typing import Optional

from sqlalchemy import delete, or_, update, text
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.class_progress import ClassProgress
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.exam import Exam
from app.models.exam_result import ExamResult
from app.models.lesson_answer import LessonAnswer
from app.models.lesson_question import LessonQuestion
from app.models.live_class import LiveClass
from app.models.note import Note
from app.models.parent_student import ParentStudent
from app.models.subject import Subject
from app.models.user import User
from app.models.chapter import LessonProgress


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

    def table_has_column(table: str, column: str) -> bool:
        try:
            result = db.execute(text(f"PRAGMA table_info('{table}')"))
        except Exception:  # pragma: no cover - defensive fallback for non-SQLite engines
            return False
        return any(row[1] == column for row in result)

    fk_refs = []
    user_fk_tables: set[str] = set()
    try:
        fk_refs = list(db.execute(text("PRAGMA foreign_key_list('users')")).mappings())
    except Exception:  # pragma: no cover - database engines without PRAGMA support
        fk_refs = []
    else:
        user_fk_tables = {ref.get("table") for ref in fk_refs if ref.get("table")}

    if user.role == "teacher":
        active_dependencies = any(
            (
                db.query(Course.id).filter(Course.teacher_id == user.id).first(),
                db.query(Subject.id).filter(Subject.instructor_id == user.id).first(),
                db.query(LiveClass.id).filter(LiveClass.teacher_id == user.id).first(),
                db.query(Exam.id).filter(Exam.teacher_id == user.id).first(),
                db.query(LessonAnswer.id).filter(LessonAnswer.teacher_id == user.id).first(),
            )
        )
        if active_dependencies:
            raise ValueError("Teacher has active assignments. Transfer responsibilities before deletion.")

    if user.role == "student":
        db.execute(delete(Enrollment).where(Enrollment.student_id == user.id))
        db.execute(delete(ClassProgress).where(ClassProgress.student_id == user.id))
        db.execute(delete(LessonProgress).where(LessonProgress.student_id == user.id))
        db.execute(delete(ExamResult).where(ExamResult.student_id == user.id))
        db.execute(delete(Note).where(Note.student_id == user.id))
        db.execute(
            update(LessonQuestion)
            .where(LessonQuestion.student_id == user.id)
            .values(student_id=None)
        )
        
        # Only delete from parent_students if the table exists
        if table_has_column("parent_students", "parent_id"):
            db.execute(
                text("DELETE FROM parent_students WHERE parent_id = :user_id OR student_id = :user_id"),
                {"user_id": user.id}
            )

        # Legacy tables may still track progress with user_id columns; remove those rows as well
        if table_has_column("class_progress", "user_id"):
            db.execute(text("DELETE FROM class_progress WHERE user_id = :user_id"), {"user_id": user.id})
        if table_has_column("lesson_progress", "user_id"):
            db.execute(text("DELETE FROM lesson_progress WHERE user_id = :user_id"), {"user_id": user.id})

    # Clean up any lingering legacy references for SQLite schemas
    for ref in fk_refs:
        table = ref.get("table")
        column = ref.get("from")
        if not table or not column:
            continue

        normalized = table.replace("_", "")
        if not normalized.isalnum():  # pragma: no cover - defensive
            continue

        # Skip self-referential entries; nothing to delete here.
        if table == "users":
            continue

        if column == "student_id":
            if table == "lesson_questions":
                db.execute(
                    text("UPDATE lesson_questions SET student_id = NULL WHERE student_id = :user_id"),
                    {"user_id": user.id},
                )
            else:
                db.execute(
                    text(f"DELETE FROM {table} WHERE {column} = :user_id"),
                    {"user_id": user.id},
                )
        elif column in {"user_id", "parent_id"}:
            db.execute(
                text(f"DELETE FROM {table} WHERE {column} = :user_id"),
                {"user_id": user.id},
            )
        elif table == "parent_students" and column == "parent_id":
            continue

    db.delete(user)
    db.commit()
