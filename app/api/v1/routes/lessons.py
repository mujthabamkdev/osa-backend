from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.api.v1.deps import get_current_user, require_role
from app.schemas.course import LessonCreate, LessonRead, LessonWithSessions
from app.models.lesson import Lesson
from app.models.subject import Subject

router = APIRouter(prefix="/subjects/{subject_id}/lessons", tags=["lessons"])


@router.get("/", response_model=List[LessonWithSessions])
def list_subject_lessons(
  subject_id: int,
  db: Session = Depends(get_db),
  _=Depends(get_current_user)
):
  """Get all lessons for a subject"""
  subject = db.query(Subject).filter(Subject.id == subject_id).first()
  if not subject:
    raise HTTPException(status_code=404, detail="Subject not found")

  lessons = db.query(Lesson).filter(
    Lesson.subject_id == subject_id
  ).order_by(Lesson.order_in_subject).all()

  return lessons


@router.post("/", response_model=LessonRead, status_code=201)
def create_lesson(
  subject_id: int,
  data: LessonCreate,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Create a new lesson for a subject"""
  subject = db.query(Subject).filter(Subject.id == subject_id).first()
  if not subject:
    raise HTTPException(status_code=404, detail="Subject not found")

  # Verify lesson's subject_id matches the URL parameter
  if data.subject_id != subject_id:
    raise HTTPException(
      status_code=400,
      detail="Lesson subject_id must match URL parameter"
    )

  lesson = Lesson(
    subject_id=data.subject_id,
    title=data.title,
    description=data.description,
    order_in_subject=data.order_in_subject
  )
  db.add(lesson)
  db.commit()
  db.refresh(lesson)
  return lesson


@router.get("/{lesson_id}", response_model=LessonWithSessions)
def get_lesson(
  subject_id: int,
  lesson_id: int,
  db: Session = Depends(get_db),
  _=Depends(get_current_user)
):
  """Get lesson details with all class sessions"""
  lesson = db.query(Lesson).filter(
    Lesson.id == lesson_id,
    Lesson.subject_id == subject_id
  ).first()
  if not lesson:
    raise HTTPException(status_code=404, detail="Lesson not found")

  return lesson


@router.put("/{lesson_id}", response_model=LessonRead)
def update_lesson(
  subject_id: int,
  lesson_id: int,
  data: LessonCreate,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Update lesson"""
  lesson = db.query(Lesson).filter(
    Lesson.id == lesson_id,
    Lesson.subject_id == subject_id
  ).first()
  if not lesson:
    raise HTTPException(status_code=404, detail="Lesson not found")

  lesson.title = data.title
  lesson.description = data.description
  lesson.order_in_subject = data.order_in_subject
  db.commit()
  db.refresh(lesson)
  return lesson


@router.delete("/{lesson_id}", status_code=204)
def delete_lesson(
  subject_id: int,
  lesson_id: int,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Delete lesson"""
  lesson = db.query(Lesson).filter(
    Lesson.id == lesson_id,
    Lesson.subject_id == subject_id
  ).first()
  if not lesson:
    raise HTTPException(status_code=404, detail="Lesson not found")

  db.delete(lesson)
  db.commit()
