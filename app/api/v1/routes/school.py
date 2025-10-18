from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.api.v1.deps import get_current_user, require_role
from app.schemas.school import (
    ClassCreate, ClassRead,
    SubjectCreate, SubjectRead,
    SessionCreate, SessionRead,
    SessionContentCreate, SessionContentRead,
    TimetableCreate, TimetableRead,
    ClassProgressCreate, ClassProgressRead
)
from app.models import (
    Class, Subject, Session, SessionContent, Timetable, ClassProgress,
    Course, User, Enrollment
)

router = APIRouter(tags=["school"])

# Classes endpoints
@router.get("/courses/{course_id}/classes", response_model=List[ClassRead])
def list_classes(course_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Get all classes for a course"""
    return db.query(Class).filter(Class.course_id == course_id).order_by(Class.year).all()

@router.post("/courses/{course_id}/classes", response_model=ClassRead, status_code=201)
def create_class(course_id: int, data: ClassCreate, db: Session = Depends(get_db), _=Depends(require_role("teacher"))):
    """Create a new class for a course"""
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Verify the class belongs to the correct course
    if data.course_id != course_id:
        raise HTTPException(status_code=400, detail="Class course_id must match URL course_id")

    new_class = Class(**data.model_dump())
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

@router.get("/classes/{class_id}", response_model=ClassRead)
def get_class(class_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Get a specific class"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_obj

# Subjects endpoints
@router.get("/classes/{class_id}/subjects", response_model=List[SubjectRead])
def list_subjects(class_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Get all subjects for a class"""
    return db.query(Subject).filter(Subject.class_id == class_id).order_by(Subject.order_in_class).all()

@router.post("/classes/{class_id}/subjects", response_model=SubjectRead, status_code=201)
def create_subject(class_id: int, data: SubjectCreate, db: Session = Depends(get_db), _=Depends(require_role("teacher"))):
    """Create a new subject for a class"""
    # Verify class exists
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Verify the subject belongs to the correct class
    if data.class_id != class_id:
        raise HTTPException(status_code=400, detail="Subject class_id must match URL class_id")

    new_subject = Subject(**data.model_dump())
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject

# Sessions endpoints
@router.get("/subjects/{subject_id}/sessions", response_model=List[SessionRead])
def list_sessions(subject_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Get all sessions for a subject"""
    return db.query(Session).filter(Session.subject_id == subject_id).order_by(Session.session_date).all()

@router.post("/subjects/{subject_id}/sessions", response_model=SessionRead, status_code=201)
def create_session(subject_id: int, data: SessionCreate, db: Session = Depends(get_db), _=Depends(require_role("teacher"))):
    """Create a new session for a subject"""
    # Verify subject exists
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Verify the session belongs to the correct subject
    if data.subject_id != subject_id:
        raise HTTPException(status_code=400, detail="Session subject_id must match URL subject_id")

    new_session = Session(**data.model_dump())
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

# Session contents endpoints
@router.get("/sessions/{session_id}/contents", response_model=List[SessionContentRead])
def list_session_contents(session_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Get all contents for a session"""
    return db.query(SessionContent).filter(SessionContent.session_id == session_id).order_by(SessionContent.order).all()

@router.post("/sessions/{session_id}/contents", response_model=SessionContentRead, status_code=201)
def create_session_content(session_id: int, data: SessionContentCreate, db: Session = Depends(get_db), _=Depends(require_role("teacher"))):
    """Create new content for a session"""
    # Verify session exists
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Verify the content belongs to the correct session
    if data.session_id != session_id:
        raise HTTPException(status_code=400, detail="Content session_id must match URL session_id")

    new_content = SessionContent(**data.model_dump())
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content

# Timetables endpoints
@router.get("/classes/{class_id}/timetable", response_model=List[TimetableRead])
def get_class_timetable(class_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Get timetable for a class"""
    return db.query(Timetable).filter(Timetable.class_id == class_id, Timetable.is_active == True).order_by(Timetable.week_day, Timetable.start_time).all()

@router.post("/timetables", response_model=TimetableRead, status_code=201)
def create_timetable(data: TimetableCreate, db: Session = Depends(get_db), _=Depends(require_role("teacher"))):
    """Create a new timetable entry"""
    new_timetable = Timetable(**data.model_dump())
    db.add(new_timetable)
    db.commit()
    db.refresh(new_timetable)
    return new_timetable

# Progress endpoints
@router.get("/students/{student_id}/progress", response_model=List[ClassProgressRead])
def get_student_progress(student_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get progress for a student (students can only see their own progress, teachers/admins can see anyone's)"""
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Students can only view their own progress")

    return db.query(ClassProgress).filter(ClassProgress.student_id == student_id).all()

@router.post("/progress", response_model=ClassProgressRead, status_code=201)
def create_progress(data: ClassProgressCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Create or update progress (students can only update their own progress)"""
    if current_user.role == "student" and current_user.id != data.student_id:
        raise HTTPException(status_code=403, detail="Students can only update their own progress")

    # Check if progress already exists
    existing = db.query(ClassProgress).filter(
        ClassProgress.student_id == data.student_id,
        ClassProgress.session_id == data.session_id
    ).first()

    if existing:
        # Update existing progress
        for key, value in data.model_dump().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new progress
        new_progress = ClassProgress(**data.model_dump())
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        return new_progress