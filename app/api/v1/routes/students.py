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

    # Get all lesson progress for the student
    from app.models.chapter import LessonProgress
    progress_records = db.query(LessonProgress).filter(LessonProgress.student_id == student_id).all()

    progress_data = []
    for progress in progress_records:
        # Get chapter information
        chapter = db.query(Chapter).filter(Chapter.id == progress.chapter_id).first()
        if chapter:
            progress_data.append({
                "chapter_id": progress.chapter_id,
                "chapter_title": chapter.title,
                "completed": progress.completed,
                "quiz_score": progress.quiz_score,
                "completed_at": progress.completed_at.isoformat() if progress.completed_at else None
            })

    return progress_data

@router.patch("/progress/{course_id}")
def update_student_progress(course_id: int, progress: int, db: Session = Depends(get_db)):
    """Update progress for a course"""
    # TODO: Implement actual progress update
    return {"message": "Progress updated", "course_id": course_id, "progress": progress}

@router.get("/{user_id}/enrolled-courses")
def get_enrolled_courses(user_id: int, db: Session = Depends(get_db)):
    """Get courses enrolled by a user"""
    # Verify user exists and is a student
    user = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get enrolled courses
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == user_id,
        Enrollment.is_active == True
    ).all()

    enrolled_courses = []
    for enrollment in enrollments:
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        if course:
            # Get active class information
            active_class_title = None
            if enrollment.active_class_id:
                active_chapter = db.query(Chapter).filter(Chapter.id == enrollment.active_class_id).first()
                if active_chapter:
                    active_class_title = active_chapter.title

            # Calculate progress statistics
            from app.models.chapter import LessonProgress
            course_chapters = db.query(Chapter).filter(Chapter.course_id == course.id).all()
            total_lessons = len(course_chapters)
            
            completed_progress = db.query(LessonProgress).filter(
                LessonProgress.student_id == user_id,
                LessonProgress.chapter_id.in_([c.id for c in course_chapters]),
                LessonProgress.completed == True
            ).all()
            completed_lessons = len(completed_progress)
            
            # Calculate overall progress percentage
            progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

            enrolled_courses.append({
                "course_id": course.id,
                "id": course.id,
                "title": course.title,
                "course_title": course.title,
                "description": course.description,
                "teacher_id": course.teacher_id,
                "enrolled_at": enrollment.enrolled_at,
                "active_class_id": enrollment.active_class_id,
                "active_class_title": active_class_title,
                "progress": progress_percentage,
                "completed_lessons": completed_lessons,
                "total_lessons": total_lessons,
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