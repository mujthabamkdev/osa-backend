from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.api.v1.deps import get_current_user, require_role
from app.schemas.course import SubjectCreate, SubjectRead, SubjectWithLessons
from app.models.subject import Subject
from app.models.course import Course
from app.models.user import User

router = APIRouter(prefix="/courses/{course_id}/subjects", tags=["subjects"])


@router.get("/", response_model=List[SubjectWithLessons])
def list_course_subjects(
  course_id: int,
  db: Session = Depends(get_db),
  _=Depends(get_current_user)
):
  """Get all subjects for a course"""
  course = db.query(Course).filter(Course.id == course_id).first()
  if not course:
    raise HTTPException(status_code=404, detail="Course not found")

  subjects = db.query(Subject).filter(
    Subject.course_id == course_id
  ).order_by(Subject.order_in_course).all()

  return subjects


@router.post("/", response_model=SubjectRead, status_code=201)
def create_subject(
  course_id: int,
  data: SubjectCreate,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Create a new subject for a course"""
  course = db.query(Course).filter(Course.id == course_id).first()
  if not course:
    raise HTTPException(status_code=404, detail="Course not found")

  # Verify course_id matches
  if data.course_id != course_id:
    raise HTTPException(
      status_code=400,
      detail="Subject course_id must match URL parameter"
    )

  # Verify instructor exists if provided
  if data.instructor_id:
    instructor = db.query(User).filter(User.id == data.instructor_id).first()
    if not instructor or instructor.role not in ("teacher", "admin"):
      raise HTTPException(
        status_code=400,
        detail="Invalid instructor_id"
      )

  subject = Subject(
    course_id=data.course_id,
    name=data.name,
    description=data.description,
    instructor_id=data.instructor_id,
    order_in_course=data.order_in_course
  )
  db.add(subject)
  db.commit()
  db.refresh(subject)
  return subject


@router.get("/{subject_id}", response_model=SubjectWithLessons)
def get_subject(
  course_id: int,
  subject_id: int,
  db: Session = Depends(get_db),
  _=Depends(get_current_user)
):
  """Get subject details with all lessons"""
  subject = db.query(Subject).filter(
    Subject.id == subject_id,
    Subject.course_id == course_id
  ).first()
  if not subject:
    raise HTTPException(status_code=404, detail="Subject not found")

  return subject


@router.put("/{subject_id}", response_model=SubjectRead)
def update_subject(
  course_id: int,
  subject_id: int,
  data: SubjectCreate,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Update subject"""
  subject = db.query(Subject).filter(
    Subject.id == subject_id,
    Subject.course_id == course_id
  ).first()
  if not subject:
    raise HTTPException(status_code=404, detail="Subject not found")

  if data.instructor_id:
    instructor = db.query(User).filter(User.id == data.instructor_id).first()
    if not instructor or instructor.role not in ("teacher", "admin"):
      raise HTTPException(
        status_code=400,
        detail="Invalid instructor_id"
      )

  subject.name = data.name
  subject.description = data.description
  subject.instructor_id = data.instructor_id
  subject.order_in_course = data.order_in_course
  db.commit()
  db.refresh(subject)
  return subject


@router.delete("/{subject_id}", status_code=204)
def delete_subject(
  course_id: int,
  subject_id: int,
  db: Session = Depends(get_db),
  _=Depends(require_role("teacher", "admin"))
):
  """Delete subject"""
  subject = db.query(Subject).filter(
    Subject.id == subject_id,
    Subject.course_id == course_id
  ).first()
  if not subject:
    raise HTTPException(status_code=404, detail="Subject not found")

  db.delete(subject)
  db.commit()
