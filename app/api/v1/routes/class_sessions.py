from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.api.v1.deps import get_current_user, require_role
from app.schemas.course import ClassSessionCreate, ClassSessionRead
from app.models.session import ClassSession
from app.models.lesson import Lesson
from datetime import date, time

router = APIRouter(
  prefix="/lessons/{lesson_id}/class-sessions",
  tags=["class-sessions"]
)


@router.get("/", response_model=List[ClassSessionRead])
def list_class_sessions(
  lesson_id: int,
  db: Session = Depends(get_db),
  _=Depends(get_current_user)
):
  """Get all class sessions for a lesson"""
  lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
  if not lesson:
    raise HTTPException(status_code=404, detail="Lesson not found")

  sessions = db.query(ClassSession).filter(
    ClassSession.lesson_id == lesson_id
  ).order_by(ClassSession.session_date, ClassSession.start_time).all()

  return sessions


@router.post("/", response_model=ClassSessionRead, status_code=201)
def create_class_session(
  lesson_id: int,
  data: ClassSessionCreate,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Create a new class session for a lesson"""
  lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
  if not lesson:
    raise HTTPException(status_code=404, detail="Lesson not found")

  # Parse date and time strings
  try:
    session_date = date.fromisoformat(data.session_date)
    start_time = time.fromisoformat(data.start_time)
    end_time = time.fromisoformat(data.end_time)
  except ValueError:
    raise HTTPException(
      status_code=400,
      detail="Invalid date/time format. Use ISO format (YYYY-MM-DD for date, HH:MM:SS for time)"
    )

  # Verify lesson_id matches
  if data.lesson_id != lesson_id:
    raise HTTPException(
      status_code=400,
      detail="Lesson ID must match URL parameter"
    )

  session = ClassSession(
    lesson_id=data.lesson_id,
    session_date=session_date,
    start_time=start_time,
    end_time=end_time,
    is_completed=data.is_completed
  )
  db.add(session)
  db.commit()
  db.refresh(session)
  return session


@router.get("/{session_id}", response_model=ClassSessionRead)
def get_class_session(
  lesson_id: int,
  session_id: int,
  db: Session = Depends(get_db),
  _=Depends(get_current_user)
):
  """Get a specific class session"""
  session = db.query(ClassSession).filter(
    ClassSession.id == session_id,
    ClassSession.lesson_id == lesson_id
  ).first()
  if not session:
    raise HTTPException(status_code=404, detail="Class session not found")

  return session


@router.put("/{session_id}", response_model=ClassSessionRead)
def update_class_session(
  lesson_id: int,
  session_id: int,
  data: ClassSessionCreate,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Update a class session"""
  session = db.query(ClassSession).filter(
    ClassSession.id == session_id,
    ClassSession.lesson_id == lesson_id
  ).first()
  if not session:
    raise HTTPException(status_code=404, detail="Class session not found")

  try:
    session.session_date = date.fromisoformat(data.session_date)
    session.start_time = time.fromisoformat(data.start_time)
    session.end_time = time.fromisoformat(data.end_time)
  except ValueError:
    raise HTTPException(
      status_code=400,
      detail="Invalid date/time format"
    )

  session.is_completed = data.is_completed
  db.commit()
  db.refresh(session)
  return session


@router.delete("/{session_id}", status_code=204)
def delete_class_session(
  lesson_id: int,
  session_id: int,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Delete a class session"""
  session = db.query(ClassSession).filter(
    ClassSession.id == session_id,
    ClassSession.lesson_id == lesson_id
  ).first()
  if not session:
    raise HTTPException(status_code=404, detail="Class session not found")

  db.delete(session)
  db.commit()
