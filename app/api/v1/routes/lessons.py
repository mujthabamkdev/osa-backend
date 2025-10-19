from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.api.v1.deps import get_current_user, require_role
from app.schemas.course import (
  LessonContentCreate,
  LessonContentRead,
  LessonContentUpdate,
  LessonCreate,
  LessonRead,
  LessonUpdate,
  LessonWithSessions,
)
from app.models.lesson import Lesson
from app.models.lesson_content import LessonContent
from app.models.subject import Subject

router = APIRouter(
  prefix="/courses/{course_id}/subjects/{subject_id}/lessons",
  tags=["lessons"]
)


@router.get("/", response_model=List[LessonWithSessions])
def list_subject_lessons(
  course_id: int,
  subject_id: int,
  db: Session = Depends(get_db),
  _=Depends(get_current_user)
):
  """Get all lessons for a subject"""
  subject = db.query(Subject).filter(
    Subject.id == subject_id,
    Subject.course_id == course_id
  ).first()
  if not subject:
    raise HTTPException(status_code=404, detail="Subject not found")

  lessons = db.query(Lesson).filter(
    Lesson.subject_id == subject_id,
    Lesson.course_id == course_id
  ).order_by(Lesson.order_in_subject).all()

  return lessons


@router.post("/", response_model=LessonRead, status_code=201)
def create_lesson(
  course_id: int,
  subject_id: int,
  data: LessonCreate,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Create a new lesson for a subject"""
  subject = db.query(Subject).filter(
    Subject.id == subject_id,
    Subject.course_id == course_id
  ).first()
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
    course_id=subject.course_id,
    title=data.title,
    description=data.description,
    scheduled_date=data.scheduled_date,
    order_in_subject=data.order_in_subject
  )
  db.add(lesson)
  db.commit()
  db.refresh(lesson)
  return lesson


@router.get("/{lesson_id}", response_model=LessonWithSessions)
def get_lesson(
  course_id: int,
  subject_id: int,
  lesson_id: int,
  db: Session = Depends(get_db),
  _=Depends(get_current_user)
):
  """Get lesson details with all class sessions"""
  lesson = db.query(Lesson).filter(
    Lesson.id == lesson_id,
    Lesson.subject_id == subject_id,
    Lesson.course_id == course_id
  ).first()
  if not lesson:
    raise HTTPException(status_code=404, detail="Lesson not found")

  return lesson


@router.put("/{lesson_id}", response_model=LessonRead)
def update_lesson(
  course_id: int,
  subject_id: int,
  lesson_id: int,
  data: LessonUpdate,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Update lesson"""
  lesson = db.query(Lesson).filter(
    Lesson.id == lesson_id,
    Lesson.subject_id == subject_id,
    Lesson.course_id == course_id
  ).first()
  if not lesson:
    raise HTTPException(status_code=404, detail="Lesson not found")

  if data.title is not None:
    lesson.title = data.title
  if data.description is not None:
    lesson.description = data.description
  if data.scheduled_date is not None:
    lesson.scheduled_date = data.scheduled_date
  if data.order_in_subject is not None:
    lesson.order_in_subject = data.order_in_subject
  db.commit()
  db.refresh(lesson)
  return lesson


@router.delete("/{lesson_id}", status_code=204)
def delete_lesson(
  course_id: int,
  subject_id: int,
  lesson_id: int,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Delete lesson"""
  lesson = db.query(Lesson).filter(
    Lesson.id == lesson_id,
    Lesson.subject_id == subject_id,
    Lesson.course_id == course_id
  ).first()
  if not lesson:
    raise HTTPException(status_code=404, detail="Lesson not found")

  db.delete(lesson)
  db.commit()


@router.get("/{lesson_id}/contents", response_model=List[LessonContentRead])
def list_lesson_contents(
  course_id: int,
  subject_id: int,
  lesson_id: int,
  db: Session = Depends(get_db),
  _=Depends(get_current_user)
):
  """List content items for a lesson"""
  lesson = db.query(Lesson).filter(
    Lesson.id == lesson_id,
    Lesson.subject_id == subject_id,
    Lesson.course_id == course_id
  ).first()
  if not lesson:
    raise HTTPException(status_code=404, detail="Lesson not found")

  return db.query(LessonContent).filter(
    LessonContent.lesson_id == lesson_id
  ).order_by(LessonContent.order_in_lesson).all()


@router.post("/{lesson_id}/contents", response_model=LessonContentRead, status_code=201)
def create_lesson_content(
  course_id: int,
  subject_id: int,
  lesson_id: int,
  data: LessonContentCreate,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Create new content for a lesson"""
  lesson = db.query(Lesson).filter(
    Lesson.id == lesson_id,
    Lesson.subject_id == subject_id,
    Lesson.course_id == course_id
  ).first()
  if not lesson:
    raise HTTPException(status_code=404, detail="Lesson not found")

  if data.lesson_id != lesson_id:
    raise HTTPException(status_code=400, detail="Content lesson_id must match URL parameter")

  content = LessonContent(
    lesson_id=data.lesson_id,
    title=data.title,
    content_type=data.content_type,
    content_url=data.content_url,
    content_text=data.content_text,
    order_in_lesson=data.order_in_lesson
  )
  db.add(content)
  db.commit()
  db.refresh(content)
  return content


@router.put("/{lesson_id}/contents/{content_id}", response_model=LessonContentRead)
def update_lesson_content(
  course_id: int,
  subject_id: int,
  lesson_id: int,
  content_id: int,
  data: LessonContentUpdate,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Update an existing lesson content item"""
  content = db.query(LessonContent).join(Lesson).filter(
    LessonContent.id == content_id,
    LessonContent.lesson_id == lesson_id,
    Lesson.subject_id == subject_id,
    Lesson.course_id == course_id
  ).first()
  if not content:
    raise HTTPException(status_code=404, detail="Content not found")

  if data.title is not None:
    content.title = data.title
  if data.content_type is not None:
    content.content_type = data.content_type
  if data.content_url is not None:
    content.content_url = data.content_url
  if data.content_text is not None:
    content.content_text = data.content_text
  if data.order_in_lesson is not None:
    content.order_in_lesson = data.order_in_lesson

  db.commit()
  db.refresh(content)
  return content


@router.delete("/{lesson_id}/contents/{content_id}", status_code=204)
def delete_lesson_content(
  course_id: int,
  subject_id: int,
  lesson_id: int,
  content_id: int,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Delete a lesson content item"""
  content = db.query(LessonContent).join(Lesson).filter(
    LessonContent.id == content_id,
    LessonContent.lesson_id == lesson_id,
    Lesson.subject_id == subject_id,
    Lesson.course_id == course_id
  ).first()
  if not content:
    raise HTTPException(status_code=404, detail="Content not found")

  db.delete(content)
  db.commit()
