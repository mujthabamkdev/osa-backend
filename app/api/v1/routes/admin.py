from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.chapter import Chapter

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics for admin"""
    total_users = db.query(User).count()
    students = db.query(User).filter(User.role == "student").count()
    teachers = db.query(User).filter(User.role == "teacher").count()
    parents = db.query(User).filter(User.role == "parent").count()
    admins = db.query(User).filter(User.role == "admin").count()

    return {
        "totalUsers": total_users,
        "students": students,
        "teachers": teachers,
        "parents": parents,
        "admins": admins,
        "totalCourses": 0,  # TODO: Implement course count
        "activeCourses": 0,  # TODO: Implement active course count
        "totalEnrollments": 0,  # TODO: Implement enrollment count
        "systemHealth": "healthy"
    }

@router.get("/users")
def get_users_by_role(role: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Get users filtered by role"""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)

    users = query.all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        for user in users
    ]

@router.get("/health")
def get_system_health(db: Session = Depends(get_db)):
    """Get system health status"""
    try:
        # Test database connection
        db.query(User).limit(1).all()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2025-10-15T00:00:00Z"  # TODO: Use actual timestamp
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": "2025-10-15T00:00:00Z"
        }

# Enrollment management endpoints
@router.post("/enroll")
def enroll_student(student_id: int, course_id: int, db: Session = Depends(get_db)):
    """Enroll a student in a course (Admin only)"""
    # Verify student exists and is a student
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id == course_id,
        Enrollment.is_active == True
    ).first()

    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Student is already enrolled in this course")

    # Create enrollment
    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id,
        is_active=True,
        active_class_id=1  # Start with Class 1 for Online Sharia course
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return {
        "message": "Student enrolled successfully",
        "enrollment_id": enrollment.id,
        "student_id": student_id,
        "course_id": course_id
    }

@router.delete("/enroll/{enrollment_id}")
def unenroll_student(enrollment_id: int, db: Session = Depends(get_db)):
    """Unenroll a student from a course (Admin only)"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    enrollment.is_active = False
    db.commit()

    return {"message": "Student unenrolled successfully"}

@router.get("/enrollments")
def get_enrollments(db: Session = Depends(get_db)):
    """Get all enrollments (Admin only)"""
    enrollments = db.query(Enrollment).filter(Enrollment.is_active == True).all()

    result = []
    for enrollment in enrollments:
        student = db.query(User).filter(User.id == enrollment.student_id).first()
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()

        result.append({
            "id": enrollment.id,
            "student": {
                "id": student.id,
                "name": student.full_name,
                "email": student.email
            },
            "course": {
                "id": course.id,
                "title": course.title,
                "teacher_id": course.teacher_id
            },
            "enrolled_at": enrollment.enrolled_at
        })

    return result


# Active class management endpoints
@router.put("/enrollments/{enrollment_id}/active-class")
def update_student_active_class(
    enrollment_id: int,
    active_class_id: int,
    db: Session = Depends(get_db)
):
    """Update a student's active class (Admin only)"""
    # Verify enrollment exists
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # Verify the chapter exists and belongs to the enrolled course
    chapter = db.query(Chapter).filter(
        Chapter.id == active_class_id,
        Chapter.course_id == enrollment.course_id
    ).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found in this course")

    # Update the active class
    enrollment.active_class_id = active_class_id
    db.commit()

    return {
        "message": "Student's active class updated successfully",
        "enrollment_id": enrollment_id,
        "student_id": enrollment.student_id,
        "active_class_id": active_class_id,
        "active_class_title": chapter.title
    }