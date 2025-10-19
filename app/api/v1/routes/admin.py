from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import require_role
from app.core.database import get_db
from app.models.chapter import Chapter
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.lesson_answer import LessonAnswer
from app.models.lesson_question import LessonQuestion
from app.models.platform_setting import PlatformSetting
from app.models.user import User
from app.schemas.admin import AdminSettings, AdminSettingsUpdate


router = APIRouter()


DEFAULT_FEATURE_FLAGS: Dict[str, bool] = {
    "allow_teacher_live_classes": True,
    "allow_teacher_exam_creation": True,
    "allow_teacher_manage_course_content": True,
    "allow_teacher_view_student_progress": True,
    "allow_parent_view_progress": True,
    "allow_parent_message_teacher": True,
    "allow_parent_download_reports": True,
    "enable_course_catalog": True,
    "enable_student_self_enrollment": True,
}


DEFAULT_ROLE_PERMISSIONS: Dict[str, Dict[str, bool]] = {
    "teacher": {
        "manage_courses": True,
        "manage_course_content": True,
        "conduct_live_classes": True,
        "create_exams": True,
        "grade_exams": True,
        "respond_to_questions": True,
        "view_student_progress": True,
        "message_parents": True,
    },
    "parent": {
        "view_child_progress": True,
        "view_grades": True,
        "download_reports": True,
        "message_teacher": True,
        "join_live_classes": False,
    },
}


def _merge_dict(defaults: Dict, overrides: Optional[Dict]) -> Dict:
    merged = {**defaults}
    if not overrides:
        return merged
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            nested_default = merged.get(key, {})
            merged[key] = {**nested_default, **value}
        else:
            merged[key] = value
    return merged


def _get_setting(db: Session, key: str, fallback: Dict) -> Dict:
    setting = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if not setting:
        setting = PlatformSetting(key=key, value=fallback)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return _merge_dict(fallback, setting.value or {})


def _save_setting(db: Session, key: str, value: Dict, description: Optional[str] = None) -> Dict:
    setting = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if setting:
        setting.value = value
        if description is not None:
            setting.description = description
    else:
        setting = PlatformSetting(key=key, value=value, description=description)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting.value


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    """Get dashboard statistics for admin"""

    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active.is_(True)).count()
    students = db.query(User).filter(User.role == "student").count()
    active_students = (
        db.query(User).filter(User.role == "student", User.is_active.is_(True)).count()
    )
    teachers = db.query(User).filter(User.role == "teacher").count()
    active_teachers = (
        db.query(User).filter(User.role == "teacher", User.is_active.is_(True)).count()
    )
    parents = db.query(User).filter(User.role == "parent").count()
    admins = db.query(User).filter(User.role == "admin").count()

    total_courses = db.query(Course).count()
    total_enrollments = db.query(Enrollment).filter(Enrollment.is_active.is_(True)).count()
    unanswered_questions = (
        db.query(LessonQuestion)
        .outerjoin(LessonAnswer, LessonAnswer.question_id == LessonQuestion.id)
        .filter(LessonAnswer.id.is_(None))
        .count()
    )

    try:
        db.query(User).limit(1).all()
        system_health = "healthy"
    except Exception:  # pragma: no cover - defensive
        system_health = "degraded"

    return {
        "totals": {
            "users": total_users,
            "activeUsers": active_users,
            "students": students,
            "teachers": teachers,
            "parents": parents,
            "admins": admins,
            "courses": total_courses,
            "enrollments": total_enrollments,
        },
        "active": {
            "students": active_students,
            "teachers": active_teachers,
        },
        "unansweredQuestions": unanswered_questions,
        "systemHealth": system_health,
        "generatedAt": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/users")
def get_users_by_role(
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """Get users filtered by role"""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)

    users = query.order_by(User.created_at.desc()).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        for user in users
    ]


@router.get("/health")
def get_system_health(db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    """Get system health status"""
    try:
        db.query(User).limit(1).all()
        db_status = "connected"
        status_str = "healthy"
        error = None
    except Exception as exc:  # pragma: no cover - defensive
        db_status = "unavailable"
        status_str = "unhealthy"
        error = str(exc)

    return {
        "status": status_str,
        "database": db_status,
        "error": error,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

# Enrollment management endpoints
@router.post("/enroll")
def enroll_student(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
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
def unenroll_student(
    enrollment_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """Unenroll a student from a course (Admin only)"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    enrollment.is_active = False
    db.commit()

    return {"message": "Student unenrolled successfully"}

@router.get("/enrollments")
def get_enrollments(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
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
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
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
        "active_class_title": chapter.title,
    }


@router.get("/settings", response_model=AdminSettings)
def get_admin_settings(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    feature_flags = _get_setting(db, "feature_flags", DEFAULT_FEATURE_FLAGS)
    role_permissions = _get_setting(db, "role_permissions", DEFAULT_ROLE_PERMISSIONS)
    return AdminSettings(feature_flags=feature_flags, role_permissions=role_permissions)


@router.put("/settings", response_model=AdminSettings)
def update_admin_settings(
    payload: AdminSettingsUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    current_flags = _get_setting(db, "feature_flags", DEFAULT_FEATURE_FLAGS)
    current_permissions = _get_setting(db, "role_permissions", DEFAULT_ROLE_PERMISSIONS)

    if payload.feature_flags is not None:
        current_flags = _merge_dict(current_flags, payload.feature_flags)
    if payload.role_permissions is not None:
        current_permissions = _merge_dict(current_permissions, payload.role_permissions)

    saved_flags = _save_setting(db, "feature_flags", current_flags, "Platform feature toggles")
    saved_permissions = _save_setting(
        db,
        "role_permissions",
        current_permissions,
        "Role permission matrix",
    )

    return AdminSettings(feature_flags=saved_flags, role_permissions=saved_permissions)


@router.post("/settings/reset", response_model=AdminSettings, status_code=status.HTTP_200_OK)
def reset_admin_settings(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    saved_flags = _save_setting(db, "feature_flags", DEFAULT_FEATURE_FLAGS)
    saved_permissions = _save_setting(db, "role_permissions", DEFAULT_ROLE_PERMISSIONS)
    return AdminSettings(feature_flags=saved_flags, role_permissions=saved_permissions)