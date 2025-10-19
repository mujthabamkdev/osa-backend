from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.note import Note
from app.models.enrollment import Enrollment
from app.models.chapter import Chapter
from app.models.chapter import Attachment
from app.models.live_class import LiveClass
from app.models.subject import Subject
from app.models.session import Session
from app.models.lesson import Lesson
from app.models.class_model import Class
from app.models.exam import Exam
from app.models.exam_result import ExamResult
from app.models.lesson_question import LessonQuestion
from app.models.lesson_answer import LessonAnswer
from app.api.v1.deps import get_current_user

# Pydantic models for request bodies
class EnrollmentRequest(BaseModel):
    course_id: int

    class Config:
        validate_assignment = True

class NoteRequest(BaseModel):
    title: str
    content: str
    course_id: Optional[int] = None
    chapter_id: Optional[int] = None

    class Config:
        validate_assignment = True


class LessonQuestionRequest(BaseModel):
    question: str
    is_anonymous: Optional[bool] = False


class LessonQuestionResponse(BaseModel):
    id: int
    question: str
    is_anonymous: bool
    answer: Optional[str]
    answered_at: Optional[datetime]
    created_at: datetime
    asked_by: Optional[int] = None


class ExamResultResponse(BaseModel):
    exam_id: int
    title: str
    description: str
    scheduled_date: Optional[datetime]
    score: Optional[int]
    max_score: Optional[int]
    status: Optional[str]
    feedback: Optional[str]
    published_at: Optional[datetime]
    course_id: int
    course_title: str

router = APIRouter()

@router.get("/courses")
def get_student_courses(db: Session = Depends(get_db)):
    """Get all courses available to students"""
    courses = db.query(Course).all()
    return [
        {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "teacher_id": course.teacher_id,
            "created_at": course.created_at
        }
        for course in courses
    ]

@router.get("/available-courses")
def get_available_courses(db: Session = Depends(get_db)):
    """Get courses available for enrollment"""
    # For now, return all courses
    courses = db.query(Course).all()
    return [
        {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "teacher_id": course.teacher_id,
            "created_at": course.created_at
        }
        for course in courses
    ]

@router.post("/enroll")
def enroll_student(enrollment_req: EnrollmentRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Enroll a student in a course"""
    try:
        course_id = enrollment_req.course_id

        # Check if course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Check if student is already enrolled
        existing = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_id,
            Enrollment.is_active == True
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Student already enrolled in this course")

        # Create enrollment
        new_enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
        db.add(new_enrollment)
        db.commit()
        db.refresh(new_enrollment)

        return {
            "id": new_enrollment.id,
            "student_id": new_enrollment.student_id,
            "course_id": new_enrollment.course_id,
            "enrolled_at": new_enrollment.enrolled_at,
            "is_active": new_enrollment.is_active,
            "message": "Enrollment successful"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Enrollment failed")

@router.delete("/unenroll/{course_id}")
def unenroll_student(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Unenroll a student from a course"""
    try:
        # Find enrollment
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_id
        ).first()

        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        # Mark as inactive instead of deleting
        enrollment.is_active = False
        db.commit()

        return {"message": "Unenrollment successful", "course_id": course_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{student_id}/progress")
def get_student_progress(student_id: int, db: Session = Depends(get_db)):
    """Get progress for a specific student"""
    # Verify student exists
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get all class progress for the student
    from app.models.class_progress import ClassProgress
    progress_records = db.query(ClassProgress).filter(ClassProgress.student_id == student_id).all()

    progress_data = []
    for progress in progress_records:
        # Get session and subject information
        session = db.query(Session).filter(Session.id == progress.session_id).first()
        subject = db.query(Subject).filter(Subject.id == progress.subject_id).first()
        if session and subject:
            progress_data.append({
                "session_id": progress.session_id,
                "session_title": session.title,
                "subject_name": subject.name,
                "completed": progress.completed,
                "score": progress.score,
                "completed_at": progress.completed_at.isoformat() if progress.completed_at else None
            })

    return progress_data

@router.patch("/progress/{course_id}")
def update_student_progress(course_id: int, progress: int, db: Session = Depends(get_db)):
    """Update progress for a course"""
    # TODO: Implement actual progress update
    return {"message": "Progress updated", "course_id": course_id, "progress": progress}

@router.get("/{student_id}/enrolled-courses")
def get_enrolled_courses(student_id: int, db: Session = Depends(get_db)):
    """Get courses enrolled by a user"""
    # Verify user exists and is a student
    user = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get enrolled courses (one enrollment per course)
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.is_active == True
    ).all()

    # Group by course_id to avoid duplicates
    courses_dict = {}
    for enrollment in enrollments:
        if enrollment.course_id not in courses_dict:
            courses_dict[enrollment.course_id] = enrollment

    enrolled_courses = []
    for course_id, enrollment in courses_dict.items():
        course = db.query(Course).filter(Course.id == course_id).first()
        if course:
            # Get the active class for this enrollment
            active_class = None
            active_class_title = None
            if enrollment.class_id:
                active_class = db.query(Class).filter(Class.id == enrollment.class_id).first()
                if active_class:
                    active_class_title = active_class.name

            # Calculate progress for the enrolled class only
            progress_percentage = 0
            total_sessions = 0
            completed_sessions = 0

            enrolled_courses.append({
                "course_id": course.id,
                "id": course.id,
                "title": course.title,
                "course_title": course.title,
                "description": course.description,
                "teacher_id": course.teacher_id,
                "enrolled_at": enrollment.enrolled_at,
                "active_class": {
                    "id": active_class.id if active_class else None,
                    "name": active_class.name if active_class else None,
                    "year": active_class.year if active_class else None
                } if active_class else None,
                "active_class_id": enrollment.class_id,
                "active_class_title": active_class_title,
                "progress": progress_percentage,
                "progress_percentage": progress_percentage,
                "completed_lessons": completed_sessions,
                "total_lessons": total_sessions,
                "last_accessed": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else ""
            })

    return enrolled_courses

@router.get("/{child_id}/academic-report")
def get_academic_report(child_id: int, db: Session = Depends(get_db)):
    """Get academic report for a child/student"""
    # Verify student exists
    student = db.query(User).filter(User.id == child_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # TODO: Implement actual academic report
    # For now, return mock report
    return {
        "child_id": child_id,
        "child_name": student.full_name,
        "total_courses": 0,
        "completed_courses": 0,
        "in_progress_courses": 0,
        "overall_progress": 0,
        "total_hours_studied": 0,
        "attendance_rate": 0,
        "last_week_activity": 0
    }

# Notes endpoints (deprecated - now course/chapter based)
# Old student-level notes endpoints removed - use /courses/{course_id}/notes instead

# Course and Chapter endpoints
@router.get("/courses/{course_id}")
def get_course_details(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed course information including chapters and attachments"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get chapters
    chapters = db.query(Chapter).filter(Chapter.course_id == course_id).order_by(Chapter.order).all()

    # Get course attachments
    course_attachments = db.query(Attachment).filter(
        Attachment.course_id == course_id,
        Attachment.chapter_id.is_(None)
    ).all()

    # Get active class information for enrolled students
    active_class = None
    if current_user.role == "student":
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_id,
            Enrollment.is_active == True
        ).first()
        if enrollment and enrollment.active_class_id:
            active_chapter = db.query(Chapter).filter(Chapter.id == enrollment.active_class_id).first()
            if active_chapter:
                active_class = {
                    "id": active_chapter.id,
                    "title": active_chapter.title,
                    "description": active_chapter.description
                }

    chapters_data = []
    for chapter in chapters:
        # Get chapter attachments
        chapter_attachments = db.query(Attachment).filter(Attachment.chapter_id == chapter.id).all()

        chapters_data.append({
            "id": chapter.id,
            "title": chapter.title,
            "description": chapter.description,
            "order": chapter.order,
            "attachments": [
                {
                    "id": attachment.id,
                    "title": attachment.title,
                    "description": attachment.description,
                    "file_url": attachment.file_url,
                    "file_type": attachment.file_type.value,
                    "file_size": attachment.file_size,
                    "duration": attachment.duration
                }
                for attachment in chapter_attachments
            ]
        })

    response = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "teacher_id": course.teacher_id,
        "created_at": course.created_at,
        "chapters": chapters_data,
        "attachments": [
            {
                "id": attachment.id,
                "title": attachment.title,
                "description": attachment.description,
                "file_url": attachment.file_url,
                "file_type": attachment.file_type.value,
                "file_size": attachment.file_size,
                "duration": attachment.duration
            }
            for attachment in course_attachments
        ]
    }

    # Add active_class if user is enrolled
    if active_class:
        response["active_class"] = active_class

    return response

# Notes endpoints (updated to be course/chapter based)
@router.get("/courses/{course_id}/notes")
def get_course_notes(course_id: int, student_id: int, db: Session = Depends(get_db)):
    """Get all notes for a course (course-level and chapter-level)"""
    # Verify student is enrolled in the course
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id == course_id,
        Enrollment.is_active == True
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Student is not enrolled in this course")

    notes = db.query(Note).filter(
        Note.student_id == student_id,
        Note.course_id == course_id
    ).all()

    return [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "course_id": note.course_id,
            "chapter_id": note.chapter_id,
            "created_at": note.created_at,
            "updated_at": note.updated_at
        }
        for note in notes
    ]

@router.post("/courses/{course_id}/notes")
def create_course_note(course_id: int, student_id: int, title: str, content: str, chapter_id: int = None, db: Session = Depends(get_db)):
    """Create a new note for a course or chapter"""
    # Verify student is enrolled in the course
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id == course_id,
        Enrollment.is_active == True
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Student is not enrolled in this course")

    # If chapter_id is provided, verify it belongs to the course
    if chapter_id:
        chapter = db.query(Chapter).filter(
            Chapter.id == chapter_id,
            Chapter.course_id == course_id
        ).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found in this course")

    new_note = Note(
        title=title,
        content=content,
        student_id=student_id,
        course_id=course_id,
        chapter_id=chapter_id
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return {
        "id": new_note.id,
        "title": new_note.title,
        "content": new_note.content,
        "course_id": new_note.course_id,
        "chapter_id": new_note.chapter_id,
        "created_at": new_note.created_at,
        "updated_at": new_note.updated_at
    }

@router.put("/courses/{course_id}/notes/{note_id}")
def update_course_note(course_id: int, note_id: int, student_id: int, title: str = None, content: str = None, db: Session = Depends(get_db)):
    """Update a course note"""
    # Verify student is enrolled in the course
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id == course_id,
        Enrollment.is_active == True
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Student is not enrolled in this course")

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.student_id == student_id,
        Note.course_id == course_id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if title is not None:
        note.title = title
    if content is not None:
        note.content = content

    db.commit()
    db.refresh(note)

    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "course_id": note.course_id,
        "chapter_id": note.chapter_id,
        "created_at": note.created_at,
        "updated_at": note.updated_at
    }

@router.delete("/courses/{course_id}/notes/{note_id}")
def delete_course_note(course_id: int, note_id: int, student_id: int, db: Session = Depends(get_db)):
    """Delete a course note"""
    # Verify student is enrolled in the course
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id == course_id,
        Enrollment.is_active == True
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Student is not enrolled in this course")

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.student_id == student_id,
        Note.course_id == course_id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()

    return {"message": "Note deleted successfully"}

# Legacy student-level notes endpoints (for compatibility with frontend)
@router.get("/{student_id}/notes")
def get_student_notes_legacy(student_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all notes for a student (legacy endpoint)"""
    # Only allow users to get their own notes (or admins)
    if current_user.id != student_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only access your own notes")

    notes = db.query(Note).filter(Note.student_id == student_id).all()

    return [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "course_id": note.course_id,
            "chapter_id": note.chapter_id,
            "created_at": note.created_at,
            "updated_at": note.updated_at
        }
        for note in notes
    ]

@router.post("/{student_id}/notes")
def create_student_note_legacy(
    student_id: int,
    title: str,
    content: str,
    course_id: int = None,
    chapter_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a note for a student (legacy endpoint)"""
    # Only allow users to create notes for themselves (or admins)
    if current_user.id != student_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only create notes for yourself")

    # If course_id provided, verify enrollment
    if course_id:
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
            Enrollment.is_active == True
        ).first()
        if not enrollment:
            raise HTTPException(status_code=403, detail="Student is not enrolled in this course")

    new_note = Note(
        title=title,
        content=content,
        student_id=student_id,
        course_id=course_id,
        chapter_id=chapter_id
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return {
        "id": new_note.id,
        "title": new_note.title,
        "content": new_note.content,
        "course_id": new_note.course_id,
        "chapter_id": new_note.chapter_id,
        "created_at": new_note.created_at,
        "updated_at": new_note.updated_at
    }

@router.put("/{student_id}/notes/{note_id}")
def update_student_note_legacy(
    student_id: int,
    note_id: int,
    title: str = None,
    content: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a student's note (legacy endpoint)"""
    # Only allow users to update their own notes (or admins)
    if current_user.id != student_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only update your own notes")

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.student_id == student_id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if title is not None:
        note.title = title
    if content is not None:
        note.content = content

    db.commit()
    db.refresh(note)

    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "course_id": note.course_id,
        "chapter_id": note.chapter_id,
        "created_at": note.created_at,
        "updated_at": note.updated_at
    }

@router.delete("/{student_id}/notes/{note_id}")
def delete_student_note_legacy(
    student_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a student's note (legacy endpoint)"""
    # Only allow users to delete their own notes (or admins)
    if current_user.id != student_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only delete your own notes")

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.student_id == student_id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()

    return {"message": "Note deleted successfully"}

# Live class timetable endpoint
@router.get("/{student_id}/timetable")
def get_student_timetable(student_id: int, date: str = None, db: Session = Depends(get_db)):
    """Get live class timetable for a student"""
    # Verify student exists
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get enrolled courses
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.is_active == True
    ).all()

    enrolled_course_ids = [e.course_id for e in enrollments]

    # Get live classes for enrolled courses
    query = db.query(LiveClass).filter(
        LiveClass.course_id.in_(enrolled_course_ids),
        LiveClass.is_active == True
    )

    if date:
        # Filter by specific date
        from datetime import datetime
        query = query.filter(LiveClass.scheduled_date == datetime.fromisoformat(date).date())

    live_classes = query.order_by(LiveClass.scheduled_date, LiveClass.start_time).all()

    result = []
    for live_class in live_classes:
        course = db.query(Course).filter(Course.id == live_class.course_id).first()
        teacher = db.query(User).filter(User.id == live_class.teacher_id).first()

        result.append({
            "id": live_class.id,
            "title": live_class.title,
            "description": live_class.description,
            "course": {
                "id": course.id,
                "title": course.title
            },
            "teacher": {
                "id": teacher.id,
                "name": teacher.full_name
            },
            "scheduled_date": live_class.scheduled_date,
            "start_time": live_class.start_time,
            "end_time": live_class.end_time,
            "meeting_link": live_class.meeting_link
        })

    return result

@router.get("/{student_id}/calendar")
def get_student_calendar(student_id: int, db: Session = Depends(get_db)):
    """Get daily calendar view of lessons for a student's enrolled courses"""
    # Verify student exists
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get enrolled courses
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.is_active == True
    ).all()

    course_ids = [e.course_id for e in enrollments]

    if not course_ids:
        return {"days": []}

    # Get lessons grouped by date
    from app.models.lesson import Lesson
    from app.models.lesson_content import LessonContent
    from app.models.subject import Subject

    lessons_query = db.query(Lesson).filter(Lesson.course_id.in_(course_ids)).order_by(Lesson.scheduled_date, Lesson.order_in_course)

    # Group lessons by date
    days_dict = {}
    for lesson in lessons_query:
        date_str = lesson.scheduled_date.isoformat()
        if date_str not in days_dict:
            days_dict[date_str] = {
                "date": date_str,
                "lessons": []
            }

        # Get subject info
        subject = db.query(Subject).filter(Subject.id == lesson.subject_id).first()
        subject_name = subject.name if subject else "Unknown"

        # Get lesson content
        content_items = db.query(LessonContent).filter(
            LessonContent.lesson_id == lesson.id
        ).order_by(LessonContent.order_in_lesson).all()

        content = []
        for item in content_items:
            content.append({
                "id": item.id,
                "type": item.content_type,
                "title": item.title,
                "url": item.content_url,
                "text": item.content_text
            })

        lesson_data = {
            "id": lesson.id,
            "title": lesson.title,
            "subject": subject_name,
            "description": lesson.description,
            "content": content
        }

        days_dict[date_str]["lessons"].append(lesson_data)

    # Convert to list and sort by date
    days = list(days_dict.values())
    days.sort(key=lambda x: x["date"])

    return {"days": days}

@router.get("/{student_id}/lessons-by-subject")
def get_lessons_by_subject(student_id: int, db: Session = Depends(get_db)):
    """Get lessons organized by subject for a student's enrolled courses"""
    # Verify student exists
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get enrolled courses
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.is_active == True
    ).all()

    course_ids = [e.course_id for e in enrollments]

    if not course_ids:
        return {"subjects": []}

    # Get all subjects for enrolled courses
    from app.models.subject import Subject
    subjects = db.query(Subject).filter(Subject.course_id.in_(course_ids)).order_by(Subject.order_in_course).all()

    subjects_data = []
    for subject in subjects:
        # Get lessons for this subject
        from app.models.lesson import Lesson
        from app.models.lesson_content import LessonContent

        lessons = db.query(Lesson).filter(
            Lesson.course_id.in_(course_ids),
            Lesson.subject_id == subject.id
        ).order_by(Lesson.scheduled_date).all()

        lessons_data = []
        for lesson in lessons:
            # Get lesson content
            content_items = db.query(LessonContent).filter(
                LessonContent.lesson_id == lesson.id
            ).order_by(LessonContent.order_in_lesson).all()

            content = []
            for item in content_items:
                content.append({
                    "id": item.id,
                    "type": item.content_type,
                    "title": item.title,
                    "url": item.content_url,
                    "text": item.content_text
                })

            lessons_data.append({
                "id": lesson.id,
                "title": lesson.title,
                "date": lesson.scheduled_date.isoformat(),
                "description": lesson.description,
                "content": content
            })

        subjects_data.append({
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "lessons": lessons_data
        })

    return {"subjects": subjects_data}


@router.post("/lessons/{lesson_id}/questions", response_model=LessonQuestionResponse, status_code=201)
def ask_lesson_question(
    lesson_id: int,
    payload: LessonQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can ask questions")

    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    subject = db.query(Subject).filter(Subject.id == lesson.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    course = db.query(Course).filter(Course.id == subject.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course.id,
            Enrollment.student_id == current_user.id,
            Enrollment.is_active == True,  # noqa: E712
        )
        .first()
    )
    if not enrollment:
        raise HTTPException(status_code=403, detail="You are not enrolled in this course")

    question = LessonQuestion(
        lesson_id=lesson_id,
        student_id=current_user.id,
        question=payload.question,
        is_anonymous=bool(payload.is_anonymous),
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return LessonQuestionResponse(
        id=question.id,
        question=question.question,
        is_anonymous=question.is_anonymous,
        answer=None,
        answered_at=None,
        created_at=question.created_at,
        asked_by=None if question.is_anonymous else question.student_id,
    )


@router.get("/lessons/{lesson_id}/questions", response_model=List[LessonQuestionResponse])
def list_lesson_questions_for_student(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    subject = db.query(Subject).filter(Subject.id == lesson.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    course = db.query(Course).filter(Course.id == subject.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "student":
        enrollment = (
            db.query(Enrollment)
            .filter(
                Enrollment.course_id == course.id,
                Enrollment.student_id == current_user.id,
                Enrollment.is_active == True,  # noqa: E712
            )
            .first()
        )
        if not enrollment:
            raise HTTPException(status_code=403, detail="You are not enrolled in this course")

    rows = (
        db.query(LessonQuestion, LessonAnswer)
        .outerjoin(LessonAnswer, LessonAnswer.question_id == LessonQuestion.id)
        .filter(LessonQuestion.lesson_id == lesson_id)
        .order_by(LessonQuestion.created_at.desc())
        .all()
    )

    responses: List[LessonQuestionResponse] = []
    for question, answer in rows:
        responses.append(
            LessonQuestionResponse(
                id=question.id,
                question=question.question,
                is_anonymous=question.is_anonymous,
                answer=answer.answer if answer else None,
                answered_at=answer.created_at if answer else None,
                created_at=question.created_at,
                asked_by=None if question.is_anonymous else question.student_id,
            )
        )

    return responses


@router.get("/me/exams", response_model=List[ExamResultResponse])
def get_my_exam_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view exam results")

    results = (
        db.query(ExamResult, Exam, Course)
        .join(Exam, Exam.id == ExamResult.exam_id)
        .join(Course, Course.id == Exam.course_id)
        .filter(
            ExamResult.student_id == current_user.id,
            Exam.is_published == True,  # noqa: E712
        )
        .order_by(Exam.scheduled_date.desc().nullslast(), Exam.created_at.desc())
        .all()
    )

    return [
        ExamResultResponse(
            exam_id=exam.id,
            title=exam.title,
            description=exam.description,
            scheduled_date=exam.scheduled_date,
            score=result.score,
            max_score=result.max_score,
            status=result.status,
            feedback=result.feedback,
            published_at=result.published_at,
            course_id=course.id,
            course_title=course.title,
        )
        for result, exam, course in results
    ]