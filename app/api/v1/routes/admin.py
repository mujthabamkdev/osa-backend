from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.deps import require_role
from app.core.database import get_db
from app.models.class_model import Class
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.exam import Exam
from app.models.live_class import LiveClass
from app.models.lesson_answer import LessonAnswer
from app.models.lesson_question import LessonQuestion
from app.models.parent_student import ParentStudent
from app.models.subject import Subject
from app.models.user import User
from app.schemas.admin import AdminSettings, AdminSettingsUpdate
from app.services.settings_service import (
    DEFAULT_SCHEDULE_CONFIG,
    get_platform_setting,
    merge_dict,
    save_platform_setting,
)


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


class PendingUserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    created_at: datetime


class CourseAssignmentPayload(BaseModel):
    course_id: int
    class_id: Optional[int] = Field(default=None, description="Optional class for the course")


class ApproveUserPayload(BaseModel):
    course_assignments: List[CourseAssignmentPayload] = Field(default_factory=list)
    child_ids: List[int] = Field(default_factory=list)
    activate: bool = True


class EnrollmentSummary(BaseModel):
    id: int
    course_id: int
    course_title: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    enrolled_at: datetime


class StudentAdminResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    enrollments: List[EnrollmentSummary] = Field(default_factory=list)


class ParentChildSummary(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None


class ParentAdminResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    children: List[ParentChildSummary] = Field(default_factory=list)


class TeacherCourseSummary(BaseModel):
    id: int
    title: str


class TeacherSubjectSummary(BaseModel):
    id: int
    name: str
    course_id: int
    course_title: str


class TeacherAssignmentOverview(BaseModel):
    teacher_id: int
    teacher_email: str
    teacher_name: Optional[str] = None
    course_count: int
    subject_count: int
    live_class_count: int
    exam_count: int
    lesson_answer_count: int
    courses: List[TeacherCourseSummary] = Field(default_factory=list)
    subjects: List[TeacherSubjectSummary] = Field(default_factory=list)


class TeacherReassignmentPayload(BaseModel):
    replacement_teacher_id: int


class TeacherReassignmentResult(BaseModel):
    deleted_teacher_id: int
    reassigned_courses: int
    reassigned_subjects: int
    reassigned_live_classes: int
    reassigned_exams: int
    reassigned_lesson_answers: int


def _serialize_enrollment(db: Session, enrollment: Enrollment) -> EnrollmentSummary:
    course = db.query(Course).filter(Course.id == enrollment.course_id).first()
    class_obj = None
    if enrollment.class_id:
        class_obj = (
            db.query(Class)
            .filter(Class.id == enrollment.class_id)
            .first()
        )

    return EnrollmentSummary(
        id=enrollment.id,
        course_id=enrollment.course_id,
        course_title=course.title if course else "Unknown Course",
        class_id=class_obj.id if class_obj else None,
        class_name=class_obj.name if class_obj else None,
        enrolled_at=enrollment.enrolled_at,
    )


def _serialize_student(db: Session, student: User) -> StudentAdminResponse:
    enrollments = (
        db.query(Enrollment)
        .filter(Enrollment.student_id == student.id, Enrollment.is_active.is_(True))
        .order_by(Enrollment.enrolled_at.desc())
        .all()
    )
    summaries = [_serialize_enrollment(db, enrollment) for enrollment in enrollments]
    return StudentAdminResponse(
        id=student.id,
        email=student.email,
        full_name=student.full_name,
        created_at=student.created_at,
        enrollments=summaries,
    )


def _serialize_parent(db: Session, parent: User) -> ParentAdminResponse:
    links = (
        db.query(ParentStudent)
        .filter(ParentStudent.parent_id == parent.id)
        .all()
    )
    child_ids = [link.student_id for link in links]
    children = []
    if child_ids:
        child_records = (
            db.query(User)
            .filter(User.id.in_(child_ids))
            .order_by(User.full_name.asc())
            .all()
        )
        children = [
            ParentChildSummary(id=child.id, email=child.email, full_name=child.full_name)
            for child in child_records
        ]

    return ParentAdminResponse(
        id=parent.id,
        email=parent.email,
        full_name=parent.full_name,
        created_at=parent.created_at,
        children=children,
    )


def _ensure_teacher_exists(db: Session, teacher_id: int) -> User:
    teacher = (
        db.query(User)
        .filter(User.id == teacher_id)
        .first()
    )
    if not teacher or teacher.role != "teacher":
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

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


@router.get("/pending-users", response_model=List[PendingUserResponse])
def get_pending_users(
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """Return all users awaiting admin approval."""

    query = db.query(User).filter(User.is_active.is_(False))
    if role:
        query = query.filter(User.role == role)

    pending_users = query.order_by(User.created_at.asc()).all()
    return [
        PendingUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            created_at=user.created_at,
        )
        for user in pending_users
    ]


@router.post("/users/{user_id}/approve", response_model=StudentAdminResponse | ParentAdminResponse)
def approve_user(
    user_id: int,
    payload: ApproveUserPayload,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """Activate an account and optionally assign courses/classes or children."""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active and payload.activate:
        raise HTTPException(status_code=400, detail="User is already active")

    user.is_active = payload.activate

    if user.role == "student":
        for assignment in payload.course_assignments:
            course = db.query(Course).filter(Course.id == assignment.course_id).first()
            if not course:
                raise HTTPException(status_code=404, detail=f"Course {assignment.course_id} not found")

            class_obj = None
            if assignment.class_id is not None:
                class_obj = (
                    db.query(Class)
                    .filter(Class.id == assignment.class_id, Class.course_id == course.id)
                    .first()
                )
                if not class_obj:
                    raise HTTPException(status_code=404, detail="Class does not belong to the selected course")

            enrollment = (
                db.query(Enrollment)
                .filter(
                    Enrollment.student_id == user.id,
                    Enrollment.course_id == course.id,
                    Enrollment.is_active.is_(True),
                )
                .first()
            )

            if enrollment:
                if assignment.class_id is not None:
                    enrollment.class_id = assignment.class_id
            else:
                db.add(
                    Enrollment(
                        student_id=user.id,
                        course_id=course.id,
                        class_id=assignment.class_id,
                        is_active=True,
                    )
                )

    if user.role == "parent":
        for child_id in payload.child_ids:
            child = (
                db.query(User)
                .filter(User.id == child_id, User.role == "student")
                .first()
            )
            if not child:
                raise HTTPException(status_code=404, detail=f"Student {child_id} not found")

            existing_link = (
                db.query(ParentStudent)
                .filter(
                    ParentStudent.parent_id == user.id,
                    ParentStudent.student_id == child.id,
                )
                .first()
            )
            if not existing_link:
                db.add(ParentStudent(parent_id=user.id, student_id=child.id))

    db.commit()
    db.refresh(user)

    if user.role == "student":
        return _serialize_student(db, user)
    if user.role == "parent":
        return _serialize_parent(db, user)

    return StudentAdminResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at,
        enrollments=[],
    )


@router.get("/students", response_model=List[StudentAdminResponse])
def list_students(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    students = (
        db.query(User)
        .filter(User.role == "student", User.is_active.is_(True))
        .order_by(User.full_name.asc(), User.created_at.asc())
        .all()
    )
    return [_serialize_student(db, student) for student in students]


class UpdateEnrollmentsPayload(BaseModel):
    course_assignments: List[CourseAssignmentPayload] = Field(default_factory=list)


@router.put("/students/{student_id}/enrollments", response_model=StudentAdminResponse)
def update_student_enrollments(
    student_id: int,
    payload: UpdateEnrollmentsPayload,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    student = (
        db.query(User)
        .filter(User.id == student_id, User.role == "student")
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = (
        db.query(Enrollment)
        .filter(Enrollment.student_id == student.id, Enrollment.is_active.is_(True))
        .all()
    )
    existing_map = {enrollment.course_id: enrollment for enrollment in existing}

    incoming_course_ids = {assignment.course_id for assignment in payload.course_assignments}

    # Deactivate enrollments not in payload
    for enrollment in existing:
        if enrollment.course_id not in incoming_course_ids:
            enrollment.is_active = False

    for assignment in payload.course_assignments:
        course = db.query(Course).filter(Course.id == assignment.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail=f"Course {assignment.course_id} not found")

        class_obj = None
        if assignment.class_id is not None:
            class_obj = (
                db.query(Class)
                .filter(Class.id == assignment.class_id, Class.course_id == course.id)
                .first()
            )
            if not class_obj:
                raise HTTPException(status_code=404, detail="Class does not belong to the selected course")

        enrollment = existing_map.get(course.id)
        if enrollment:
            enrollment.is_active = True
            enrollment.class_id = assignment.class_id
        else:
            db.add(
                Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    class_id=assignment.class_id,
                    is_active=True,
                )
            )

    db.commit()
    return _serialize_student(db, student)


class UpdateParentChildrenPayload(BaseModel):
    child_ids: List[int] = Field(default_factory=list)


@router.get("/parents", response_model=List[ParentAdminResponse])
def list_parents(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    parents = (
        db.query(User)
        .filter(User.role == "parent", User.is_active.is_(True))
        .order_by(User.full_name.asc(), User.created_at.asc())
        .all()
    )
    return [_serialize_parent(db, parent) for parent in parents]


@router.put("/parents/{parent_id}/children", response_model=ParentAdminResponse)
def update_parent_children(
    parent_id: int,
    payload: UpdateParentChildrenPayload,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    parent = (
        db.query(User)
        .filter(User.id == parent_id, User.role == "parent")
        .first()
    )
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    desired_ids = set(payload.child_ids)

    # Remove links no longer present
    existing_links = (
        db.query(ParentStudent)
        .filter(ParentStudent.parent_id == parent.id)
        .all()
    )
    for link in existing_links:
        if link.student_id not in desired_ids:
            db.delete(link)

    # Add missing links
    current_student_ids = {link.student_id for link in existing_links}
    for child_id in desired_ids:
        if child_id in current_student_ids:
            continue
        child = (
            db.query(User)
            .filter(User.id == child_id, User.role == "student")
            .first()
        )
        if not child:
            raise HTTPException(status_code=404, detail=f"Student {child_id} not found")
        db.add(ParentStudent(parent_id=parent.id, student_id=child.id))

    db.commit()
    return _serialize_parent(db, parent)


@router.get("/teachers/{teacher_id}/assignments", response_model=TeacherAssignmentOverview)
def get_teacher_assignments(
    teacher_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    teacher = _ensure_teacher_exists(db, teacher_id)

    courses = (
        db.query(Course)
        .filter(Course.teacher_id == teacher.id)
        .order_by(Course.title.asc())
        .all()
    )

    subjects = (
        db.query(Subject, Course)
        .join(Course, Course.id == Subject.course_id)
        .filter(Subject.instructor_id == teacher.id)
        .order_by(Course.title.asc(), Subject.order_in_course.asc())
        .all()
    )

    live_class_count = (
        db.query(func.count(LiveClass.id))
        .filter(LiveClass.teacher_id == teacher.id)
        .scalar()
        or 0
    )
    exam_count = (
        db.query(func.count(Exam.id))
        .filter(Exam.teacher_id == teacher.id)
        .scalar()
        or 0
    )
    lesson_answer_count = (
        db.query(func.count(LessonAnswer.id))
        .filter(LessonAnswer.teacher_id == teacher.id)
        .scalar()
        or 0
    )

    return TeacherAssignmentOverview(
        teacher_id=teacher.id,
        teacher_email=teacher.email,
        teacher_name=teacher.full_name,
        course_count=len(courses),
        subject_count=len(subjects),
        live_class_count=live_class_count,
        exam_count=exam_count,
        lesson_answer_count=lesson_answer_count,
        courses=[
            TeacherCourseSummary(id=course.id, title=course.title)
            for course in courses
        ],
        subjects=[
            TeacherSubjectSummary(
                id=subject.id,
                name=subject.name,
                course_id=course.id,
                course_title=course.title,
            )
            for subject, course in subjects
        ],
    )


@router.post("/teachers/{teacher_id}/reassign", response_model=TeacherReassignmentResult)
def reassign_teacher_and_delete(
    teacher_id: int,
    payload: TeacherReassignmentPayload,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    teacher = _ensure_teacher_exists(db, teacher_id)

    if teacher_id == payload.replacement_teacher_id:
        raise HTTPException(status_code=400, detail="Replacement teacher must be different")

    replacement = _ensure_teacher_exists(db, payload.replacement_teacher_id)

    if not replacement.is_active:
        raise HTTPException(status_code=400, detail="Replacement teacher must be active")

    courses_updated = (
        db.query(Course)
        .filter(Course.teacher_id == teacher.id)
        .update({Course.teacher_id: replacement.id}, synchronize_session=False)
    )
    subjects_updated = (
        db.query(Subject)
        .filter(Subject.instructor_id == teacher.id)
        .update({Subject.instructor_id: replacement.id}, synchronize_session=False)
    )
    live_classes_updated = (
        db.query(LiveClass)
        .filter(LiveClass.teacher_id == teacher.id)
        .update({LiveClass.teacher_id: replacement.id}, synchronize_session=False)
    )
    exams_updated = (
        db.query(Exam)
        .filter(Exam.teacher_id == teacher.id)
        .update({Exam.teacher_id: replacement.id}, synchronize_session=False)
    )
    lesson_answers_updated = (
        db.query(LessonAnswer)
        .filter(LessonAnswer.teacher_id == teacher.id)
        .update({LessonAnswer.teacher_id: replacement.id}, synchronize_session=False)
    )

    db.flush()

    db.delete(teacher)
    db.commit()

    return TeacherReassignmentResult(
        deleted_teacher_id=teacher_id,
        reassigned_courses=courses_updated,
        reassigned_subjects=subjects_updated,
        reassigned_live_classes=live_classes_updated,
        reassigned_exams=exams_updated,
        reassigned_lesson_answers=lesson_answers_updated,
    )
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
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """Enroll a student in a course (Admin only).

    Deprecated in favor of /students/{id}/enrollments but kept for compatibility.
    """
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
        if class_id is not None:
            class_obj = (
                db.query(Class)
                .filter(Class.id == class_id, Class.course_id == course.id)
                .first()
            )
            if not class_obj:
                raise HTTPException(status_code=404, detail="Class does not belong to selected course")
            existing_enrollment.class_id = class_id
            db.commit()
            db.refresh(existing_enrollment)
        else:
            raise HTTPException(status_code=400, detail="Student is already enrolled in this course")

        return {
            "message": "Enrollment updated",
            "enrollment_id": existing_enrollment.id,
            "student_id": student_id,
            "course_id": course_id,
            "class_id": existing_enrollment.class_id,
        }

    if class_id is not None:
        class_obj = (
            db.query(Class)
            .filter(Class.id == class_id, Class.course_id == course.id)
            .first()
        )
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class does not belong to selected course")

    # Create enrollment
    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id,
        class_id=class_id,
        is_active=True,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return {
        "message": "Student enrolled successfully",
        "enrollment_id": enrollment.id,
        "student_id": student_id,
        "course_id": course_id,
        "class_id": enrollment.class_id,
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
@router.put("/enrollments/{enrollment_id}/class")
def update_student_class(
    enrollment_id: int,
    class_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """Update a student's active class (Admin only)"""
    # Verify enrollment exists
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    class_obj = (
        db.query(Class)
        .filter(Class.id == class_id, Class.course_id == enrollment.course_id)
        .first()
    )
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found in this course")

    # Update the active class
    enrollment.class_id = class_id
    db.commit()

    return {
        "message": "Student's active class updated successfully",
        "enrollment_id": enrollment_id,
        "student_id": enrollment.student_id,
        "class_id": class_id,
        "class_name": class_obj.name,
    }


@router.get("/settings", response_model=AdminSettings)
def get_admin_settings(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    feature_flags = get_platform_setting(db, "feature_flags", DEFAULT_FEATURE_FLAGS)
    role_permissions = get_platform_setting(db, "role_permissions", DEFAULT_ROLE_PERMISSIONS)
    schedule_config = get_platform_setting(db, "schedule_config", DEFAULT_SCHEDULE_CONFIG)
    return AdminSettings(
        feature_flags=feature_flags,
        role_permissions=role_permissions,
        schedule_config=schedule_config,
    )


@router.put("/settings", response_model=AdminSettings)
def update_admin_settings(
    payload: AdminSettingsUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    current_flags = get_platform_setting(db, "feature_flags", DEFAULT_FEATURE_FLAGS)
    current_permissions = get_platform_setting(db, "role_permissions", DEFAULT_ROLE_PERMISSIONS)
    current_schedule = get_platform_setting(db, "schedule_config", DEFAULT_SCHEDULE_CONFIG)

    if payload.feature_flags is not None:
        current_flags = merge_dict(current_flags, payload.feature_flags)
    if payload.role_permissions is not None:
        current_permissions = merge_dict(current_permissions, payload.role_permissions)
    if payload.schedule_config is not None:
        current_schedule = merge_dict(current_schedule, payload.schedule_config)

    saved_flags = save_platform_setting(db, "feature_flags", current_flags, "Platform feature toggles")
    saved_permissions = save_platform_setting(
        db,
        "role_permissions",
        current_permissions,
        "Role permission matrix",
    )
    saved_schedule = save_platform_setting(
        db,
        "schedule_config",
        current_schedule,
        "Class scheduling configuration",
    )

    return AdminSettings(
        feature_flags=saved_flags,
        role_permissions=saved_permissions,
        schedule_config=saved_schedule,
    )


@router.post("/settings/reset", response_model=AdminSettings, status_code=status.HTTP_200_OK)
def reset_admin_settings(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    saved_flags = save_platform_setting(db, "feature_flags", DEFAULT_FEATURE_FLAGS)
    saved_permissions = save_platform_setting(db, "role_permissions", DEFAULT_ROLE_PERMISSIONS)
    saved_schedule = save_platform_setting(db, "schedule_config", DEFAULT_SCHEDULE_CONFIG)
    return AdminSettings(
        feature_flags=saved_flags,
        role_permissions=saved_permissions,
        schedule_config=saved_schedule,
    )