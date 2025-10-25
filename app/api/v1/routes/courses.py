from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.api.v1.deps import get_current_user, require_role
from app.schemas.course import CourseCreate, CourseRead
from app.models.course import Course
from app.models.user import User
from app.models.chapter import Chapter, Attachment, Quiz, QuizQuestion, LessonProgress
from app.models.subject import Subject
from app.models.live_class import LiveClass
from app.models.enrollment import Enrollment
from app.models.class_model import Class
from app.services.courses import create_course
from app.services.settings_service import DEFAULT_SCHEDULE_CONFIG, get_platform_setting
import json
from datetime import datetime

router = APIRouter(tags=["courses"])

@router.get("/", response_model=List[CourseRead])
def list_courses(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Course).order_by(Course.id.asc()).all()

@router.post("/", response_model=CourseRead, status_code=201)
def create_course_endpoint(data: CourseCreate, db: Session = Depends(get_db), _=Depends(require_role("teacher"))):
    teacher = db.query(User).filter(User.id == data.teacher_id).first()
    if not teacher or teacher.role not in ("teacher","admin"):
        raise HTTPException(status_code=400, detail="Invalid teacher_id")
    return create_course(db, title=data.title, description=data.description, teacher_id=data.teacher_id)

# Course details endpoints
@router.get("/{course_id}")
def get_course_details(course_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get detailed course information with chapters, attachments, live classes, and progress"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get teacher details
    teacher = db.query(User).filter(User.id == course.teacher_id).first()
    teacher_data = None
    if teacher:
        teacher_data = {
            "id": teacher.id,
            "email": teacher.email,
            "full_name": teacher.full_name,
            "role": teacher.role
        }

    # Get student's active class if enrolled
    active_class_data = None
    if current_user.role == "student":
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_id,
            Enrollment.is_active == True
        ).first()
        if enrollment and enrollment.class_id:
            active_class = db.query(Class).filter(Class.id == enrollment.class_id).first()
            if active_class:
                active_class_data = {
                    "id": active_class.id,
                    "year": active_class.year,
                    "name": active_class.name,
                    "is_active": active_class.is_active
                }

    # Get classes for this course
    classes = db.query(Class).filter(Class.course_id == course_id).order_by(Class.year).all()

    classes_data = []
    for class_obj in classes:
        # For the new structure, classes don't have subjects directly
        # Subjects now belong to courses
        classes_data.append({
            "id": class_obj.id,
            "year": class_obj.year,
            "name": class_obj.name,
            "is_active": class_obj.is_active,
            "subjects": []  # Classes no longer have subjects directly
        })

    # Get subjects for this course (new structure)
    subjects = db.query(Subject).filter(Subject.course_id == course_id).order_by(Subject.order_in_course).all()

    subjects_data = []
    for subject in subjects:
        # Get lessons for this subject
        from app.models.lesson import Lesson
        from app.models.lesson_content import LessonContent

        lessons = db.query(Lesson).filter(
            Lesson.subject_id == subject.id
        ).order_by(Lesson.scheduled_date, Lesson.order_in_subject).all()

        lessons_data = []
        for lesson in lessons:
            # Get lesson content
            contents = db.query(LessonContent).filter(LessonContent.lesson_id == lesson.id).order_by(LessonContent.order_in_lesson).all()

            lessons_data.append({
                "id": lesson.id,
                "title": lesson.title,
                "description": lesson.description,
                "scheduled_date": lesson.scheduled_date.isoformat() if lesson.scheduled_date else None,
                "order_in_subject": lesson.order_in_subject,
                "contents": [{
                    "id": content.id,
                    "title": content.title,
                    "content_type": content.content_type,
                    "content_url": content.content_url,
                    "content_text": content.content_text,
                    "order_in_lesson": content.order_in_lesson
                } for content in contents]
            })

        subjects_data.append({
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "instructor_id": subject.instructor_id,
            "order_in_course": subject.order_in_course,
            "lessons": lessons_data
        })

    # Get live classes for this course
    live_classes = db.query(LiveClass).filter(
        LiveClass.course_id == course_id,
        LiveClass.is_active == True
    ).order_by(LiveClass.scheduled_date).all()

    live_classes_data = [
        {
            "id": lc.id,
            "title": lc.title,
            "description": lc.description,
            "chapter_id": lc.chapter_id,
            "scheduled_date": lc.scheduled_date.isoformat(),
            "start_time": lc.start_time.isoformat(),
            "end_time": lc.end_time.isoformat(),
            "meeting_link": lc.meeting_link
        } for lc in live_classes
    ]

    schedule_config = get_platform_setting(db, "schedule_config", DEFAULT_SCHEDULE_CONFIG)

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "teacher_id": course.teacher_id,
        "teacher": teacher_data,
        "active_class": active_class_data,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "classes": classes_data,
        "subjects": subjects_data,
        "live_classes": live_classes_data,
        "schedule_config": schedule_config,
    }
