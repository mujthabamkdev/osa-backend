from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.api.v1.deps import get_current_user, require_role
from app.schemas.course import CourseCreate, CourseRead
from app.models.course import Course
from app.models.user import User
from app.models.chapter import Chapter, Attachment, Quiz, QuizQuestion, LessonProgress
from app.models.live_class import LiveClass
from app.models.enrollment import Enrollment
from app.services.courses import create_course
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
        if enrollment and enrollment.active_class_id:
            active_chapter = db.query(Chapter).filter(Chapter.id == enrollment.active_class_id).first()
            if active_chapter:
                active_class_data = {
                    "id": active_chapter.id,
                    "title": active_chapter.title,
                    "description": active_chapter.description
                }

    # Get chapters
    chapters = db.query(Chapter).filter(Chapter.course_id == course_id).order_by(Chapter.order).all()

    chapters_data = []
    for chapter in chapters:
        # Get attachments for this chapter
        attachments = db.query(Attachment).filter(Attachment.chapter_id == chapter.id).order_by(Attachment.id).all()

        # Get quiz for this chapter
        quiz = db.query(Quiz).filter(Quiz.chapter_id == chapter.id).first()
        quiz_data = None
        if quiz:
            questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).order_by(QuizQuestion.order).all()
            quiz_data = {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "passing_score": quiz.passing_score,
                "questions": [
                    {
                        "id": q.id,
                        "question": q.question,
                        "options": json.loads(q.options),
                        "correct_answer": q.correct_answer,
                        "order": q.order
                    } for q in questions
                ]
            }

        # Get progress for current user
        progress = None
        if current_user.role == "student":
            progress = db.query(LessonProgress).filter(
                LessonProgress.student_id == current_user.id,
                LessonProgress.chapter_id == chapter.id
            ).first()
            if progress:
                progress = {
                    "completed": progress.completed,
                    "quiz_score": progress.quiz_score,
                    "completed_at": progress.completed_at.isoformat() if progress.completed_at else None
                }

        chapters_data.append({
            "id": chapter.id,
            "title": chapter.title,
            "description": chapter.description,
            "order": chapter.order,
            "attachments": [
                {
                    "id": att.id,
                    "title": att.title,
                    "file_type": att.file_type,
                    "file_url": att.file_url,
                    "source": att.source,
                    "description": att.description
                } for att in attachments
            ],
            "quiz": quiz_data,
            "progress": progress
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

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "teacher_id": course.teacher_id,
        "teacher": teacher_data,
        "active_class": active_class_data,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "chapters": chapters_data,
        "live_classes": live_classes_data
    }

@router.post("/{course_id}/chapters/{chapter_id}/complete")
def complete_lesson(course_id: int, chapter_id: int, quiz_score: int = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Mark a lesson as completed"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can complete lessons")

    # Verify chapter belongs to course
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id, Chapter.course_id == course_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Check if quiz exists and score meets requirements
    quiz = db.query(Quiz).filter(Quiz.chapter_id == chapter_id).first()
    if quiz and quiz_score is not None and quiz_score < quiz.passing_score:
        raise HTTPException(status_code=400, detail=f"Quiz score {quiz_score}% does not meet passing score of {quiz.passing_score}%")

    # Update or create progress
    progress = db.query(LessonProgress).filter(
        LessonProgress.student_id == current_user.id,
        LessonProgress.chapter_id == chapter_id
    ).first()

    from datetime import datetime
    if progress:
        progress.completed = True
        progress.quiz_score = quiz_score
        progress.completed_at = datetime.utcnow()
    else:
        new_progress = LessonProgress(
            student_id=current_user.id,
            chapter_id=chapter_id,
            completed=True,
            quiz_score=quiz_score,
            completed_at=datetime.utcnow()
        )
        db.add(new_progress)

    db.commit()
    return {"message": "Lesson completed successfully"}

@router.get("/{course_id}/progress")
def get_course_progress(course_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get student's progress for a course"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view progress")

    # Get all chapters for the course
    chapters = db.query(Chapter).filter(Chapter.course_id == course_id).all()
    total_chapters = len(chapters)

    # Get completed chapters
    completed_progress = db.query(LessonProgress).filter(
        LessonProgress.student_id == current_user.id,
        LessonProgress.chapter_id.in_([c.id for c in chapters]),
        LessonProgress.completed == True
    ).all()

    completed_chapters = len(completed_progress)
    progress_percentage = (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0

    return {
        "course_id": course_id,
        "total_chapters": total_chapters,
        "completed_chapters": completed_chapters,
        "progress_percentage": round(progress_percentage, 1),
        "completed_lessons": [
            {
                "chapter_id": p.chapter_id,
                "quiz_score": p.quiz_score,
                "completed_at": p.completed_at
            } for p in completed_progress
        ]
    }
