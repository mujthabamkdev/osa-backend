from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.v1.deps import require_role
from app.core.database import get_db
from app.models import (
  Course,
  Subject,
  Lesson,
  Enrollment,
  LiveClass,
  LessonQuestion,
  LessonAnswer,
  Exam,
  ExamResult,
  User,
)
from app.models.class_progress import ClassProgress
from app.models.session import Session as LegacySession
from app.schemas.course import CourseRead
from app.schemas.teacher import (
  TeacherOverview,
  TeacherStudent,
  TeacherSubject,
  ExamCreate,
  ExamRead,
  ExamResultBulkCreate,
  ExamResultRead,
  LiveClassCreate,
  LiveClassRead,
  LessonAnswerCreate,
  LessonAnswerRead,
  LessonQuestionRead,
  StudentProgressEntry,
  StudentReport,
)

router = APIRouter()


def _get_teacher_course_ids(db: Session, teacher_id: int) -> List[int]:
  return [row.id for row in db.query(Course.id).filter(Course.teacher_id == teacher_id).all()]


def _get_teacher_subject_ids(db: Session, teacher_id: int, course_ids: List[int]) -> List[int]:
  if not course_ids:
    return []
  return [
    row.id
    for row in db.query(Subject.id).filter(
      or_(Subject.course_id.in_(course_ids), Subject.instructor_id == teacher_id)
    ).all()
  ]


def _ensure_course_access(course_id: int, course_ids: List[int]) -> None:
  if course_id not in course_ids:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Course not assigned to you")


def _ensure_student_in_courses(db: Session, student_id: int, course_ids: List[int]) -> None:
  enrollment_exists = (
    db.query(Enrollment)
    .filter(
      Enrollment.student_id == student_id,
      Enrollment.course_id.in_(course_ids),
      Enrollment.is_active == True,  # noqa: E712
    )
    .first()
  )
  if not enrollment_exists:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found in your courses")


@router.get("/overview", response_model=TeacherOverview)
def get_teacher_overview(
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> TeacherOverview:
  course_ids = _get_teacher_course_ids(db, current_user.id)
  subject_ids = _get_teacher_subject_ids(db, current_user.id, course_ids)

  if not course_ids:
    return TeacherOverview()

  total_students = (
    db.query(func.count(func.distinct(Enrollment.student_id)))
    .filter(
      Enrollment.course_id.in_(course_ids),
      Enrollment.is_active == True,  # noqa: E712
    )
    .scalar()
    or 0
  )

  total_subjects = len(subject_ids)

  upcoming_live_classes = (
    db.query(func.count(LiveClass.id))
    .filter(
      LiveClass.course_id.in_(course_ids),
      LiveClass.is_active == True,  # noqa: E712
      LiveClass.scheduled_date >= datetime.utcnow(),
    )
    .scalar()
    or 0
  )

  pending_questions = 0
  if subject_ids:
    lesson_ids = [row.id for row in db.query(Lesson.id).filter(Lesson.subject_id.in_(subject_ids)).all()]
    if lesson_ids:
      pending_questions = (
        db.query(func.count(LessonQuestion.id))
        .outerjoin(LessonAnswer, LessonAnswer.question_id == LessonQuestion.id)
        .filter(
          LessonQuestion.lesson_id.in_(lesson_ids),
          LessonAnswer.id.is_(None),
        )
        .scalar()
        or 0
      )

  return TeacherOverview(
    total_students=total_students,
    total_subjects=total_subjects,
    total_courses=len(course_ids),
    upcoming_live_classes=upcoming_live_classes,
    pending_questions=pending_questions,
  )


@router.get("/courses", response_model=List[CourseRead])
def get_teacher_courses(
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> List[CourseRead]:
  courses = db.query(Course).filter(Course.teacher_id == current_user.id).all()
  return [CourseRead.model_validate(course) for course in courses]


@router.get("/students", response_model=List[TeacherStudent])
def list_teacher_students(
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> List[TeacherStudent]:
  query = (
    db.query(User, Course, Enrollment)
    .join(Enrollment, Enrollment.student_id == User.id)
    .join(Course, Course.id == Enrollment.course_id)
    .filter(
      Course.teacher_id == current_user.id,
      Enrollment.is_active == True,  # noqa: E712
      User.role == "student",
    )
    .order_by(User.full_name.is_(None), User.full_name, User.email)
  )

  students: List[TeacherStudent] = []
  for student, course, enrollment in query.all():
    students.append(
      TeacherStudent(
        id=student.id,
        email=student.email,
        full_name=student.full_name,
        course_id=course.id,
        course_title=course.title,
      )
    )
  return students


@router.get("/courses/{course_id}/students", response_model=List[TeacherStudent])
def list_students_by_course(
  course_id: int,
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> List[TeacherStudent]:
  course_ids = _get_teacher_course_ids(db, current_user.id)
  _ensure_course_access(course_id, course_ids)

  query = (
    db.query(User, Course)
    .join(Enrollment, Enrollment.student_id == User.id)
    .join(Course, Course.id == Enrollment.course_id)
    .filter(
      Course.id == course_id,
      Enrollment.is_active == True,  # noqa: E712
      User.role == "student",
    )
    .order_by(User.full_name.is_(None), User.full_name, User.email)
  )

  return [
    TeacherStudent(
      id=student.id,
      email=student.email,
      full_name=student.full_name,
      course_id=course.id,
      course_title=course.title,
    )
    for student, course in query.all()
  ]


@router.get("/subjects", response_model=List[TeacherSubject])
def list_teacher_subjects(
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> List[TeacherSubject]:
  course_ids = _get_teacher_course_ids(db, current_user.id)
  if not course_ids:
    return []

  subjects = (
    db.query(Subject, Course)
    .join(Course, Course.id == Subject.course_id)
    .filter(
      or_(Subject.instructor_id == current_user.id, Subject.course_id.in_(course_ids))
    )
    .order_by(Course.title, Subject.order_in_course)
  ).all()

  return [
    TeacherSubject(
      id=subject.id,
      name=subject.name,
      course_id=course.id,
      course_title=course.title,
    )
    for subject, course in subjects
  ]


@router.post("/exams", response_model=ExamRead, status_code=status.HTTP_201_CREATED)
def create_exam(
  payload: ExamCreate,
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> ExamRead:
  course_ids = _get_teacher_course_ids(db, current_user.id)
  _ensure_course_access(payload.course_id, course_ids)

  if payload.subject_id:
    subject = db.query(Subject).filter(Subject.id == payload.subject_id).first()
    if not subject or subject.course_id != payload.course_id:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject does not belong to course")

  exam = Exam(
    course_id=payload.course_id,
    subject_id=payload.subject_id,
    teacher_id=current_user.id,
    title=payload.title,
    description=payload.description,
    scheduled_date=payload.scheduled_date,
    duration_minutes=payload.duration_minutes,
    max_score=payload.max_score,
  )

  db.add(exam)
  db.commit()
  db.refresh(exam)
  return ExamRead.model_validate(exam)


@router.get("/exams", response_model=List[ExamRead])
def list_teacher_exams(
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> List[ExamRead]:
  exams = db.query(Exam).filter(Exam.teacher_id == current_user.id).order_by(Exam.created_at.desc()).all()
  return [ExamRead.model_validate(exam) for exam in exams]


@router.get("/exams/{exam_id}", response_model=ExamRead)
def get_exam(
  exam_id: int,
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> ExamRead:
  exam = db.query(Exam).filter(Exam.id == exam_id, Exam.teacher_id == current_user.id).first()
  if not exam:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
  return ExamRead.model_validate(exam)


@router.get("/exams/{exam_id}/results", response_model=List[ExamResultRead])
def list_exam_results(
  exam_id: int,
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> List[ExamResultRead]:
  exam = db.query(Exam).filter(Exam.id == exam_id, Exam.teacher_id == current_user.id).first()
  if not exam:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")

  results = db.query(ExamResult).filter(ExamResult.exam_id == exam_id).all()
  return [ExamResultRead.model_validate(result) for result in results]


@router.post("/exams/{exam_id}/results", response_model=List[ExamResultRead])
def upsert_exam_results(
  exam_id: int,
  payload: ExamResultBulkCreate,
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> List[ExamResultRead]:
  exam = db.query(Exam).filter(Exam.id == exam_id, Exam.teacher_id == current_user.id).first()
  if not exam:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")

  course_ids = _get_teacher_course_ids(db, current_user.id)
  _ensure_course_access(exam.course_id, course_ids)

  results: List[ExamResult] = []
  now = datetime.utcnow()

  for result_payload in payload.results:
    _ensure_student_in_courses(db, result_payload.student_id, [exam.course_id])

    result = (
      db.query(ExamResult)
      .filter(
        ExamResult.exam_id == exam_id,
        ExamResult.student_id == result_payload.student_id,
      )
      .first()
    )

    if result:
      result.score = result_payload.score
      result.max_score = result_payload.max_score
      result.status = result_payload.status
      result.feedback = result_payload.feedback
      result.published_at = result_payload.published_at or now
    else:
      result = ExamResult(
        exam_id=exam_id,
        student_id=result_payload.student_id,
        score=result_payload.score,
        max_score=result_payload.max_score,
        status=result_payload.status,
        feedback=result_payload.feedback,
        published_at=result_payload.published_at or now,
      )
      db.add(result)
    results.append(result)

  exam.is_published = True
  db.commit()

  for result in results:
    db.refresh(result)

  return [ExamResultRead.model_validate(result) for result in results]


@router.post("/live-classes", response_model=LiveClassRead, status_code=status.HTTP_201_CREATED)
def schedule_live_class(
  payload: LiveClassCreate,
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> LiveClassRead:
  course_ids = _get_teacher_course_ids(db, current_user.id)
  _ensure_course_access(payload.course_id, course_ids)

  live_class = LiveClass(
    course_id=payload.course_id,
    chapter_id=payload.chapter_id,
    title=payload.title,
    description=payload.description,
    scheduled_date=payload.scheduled_date,
    start_time=payload.start_time,
    end_time=payload.end_time,
    meeting_link=payload.meeting_link,
    teacher_id=current_user.id,
    is_active=True,
  )

  db.add(live_class)
  db.commit()
  db.refresh(live_class)
  return LiveClassRead.model_validate(live_class)


@router.get("/live-classes", response_model=List[LiveClassRead])
def list_live_classes(
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> List[LiveClassRead]:
  classes = (
    db.query(LiveClass)
    .filter(LiveClass.teacher_id == current_user.id)
    .order_by(LiveClass.scheduled_date.desc(), LiveClass.start_time.desc())
    .all()
  )
  return [LiveClassRead.model_validate(live_class) for live_class in classes]


@router.get("/lessons/{lesson_id}/questions", response_model=List[LessonQuestionRead])
def list_lesson_questions(
  lesson_id: int,
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> List[LessonQuestionRead]:
  lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
  if not lesson:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

  subject = db.query(Subject).filter(Subject.id == lesson.subject_id).first()
  if not subject:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

  course = db.query(Course).filter(Course.id == subject.course_id, Course.teacher_id == current_user.id).first()
  if not course:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this lesson")

  rows = (
    db.query(LessonQuestion, LessonAnswer)
    .outerjoin(LessonAnswer, LessonAnswer.question_id == LessonQuestion.id)
    .filter(LessonQuestion.lesson_id == lesson_id)
    .order_by(LessonQuestion.created_at.desc())
    .all()
  )

  data: List[LessonQuestionRead] = []
  for question, answer in rows:
    data.append(
      LessonQuestionRead(
        id=question.id,
        lesson_id=question.lesson_id,
        question=question.question,
        student_id=question.student_id,
        is_anonymous=question.is_anonymous,
        created_at=question.created_at,
        answer=answer.answer if answer else None,
        answered_by=answer.teacher_id if answer else None,
        answered_at=answer.created_at if answer else None,
      )
    )
  return data


@router.post("/lessons/{lesson_id}/questions/{question_id}/answers", response_model=LessonAnswerRead, status_code=status.HTTP_201_CREATED)
def answer_lesson_question(
  lesson_id: int,
  question_id: int,
  payload: LessonAnswerCreate,
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> LessonAnswerRead:
  lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
  if not lesson:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

  subject = db.query(Subject).filter(Subject.id == lesson.subject_id).first()
  if not subject:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

  course = db.query(Course).filter(Course.id == subject.course_id, Course.teacher_id == current_user.id).first()
  if not course:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this lesson")

  question = (
    db.query(LessonQuestion)
    .filter(LessonQuestion.id == question_id, LessonQuestion.lesson_id == lesson_id)
    .first()
  )
  if not question:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

  existing_answer = (
    db.query(LessonAnswer)
    .filter(LessonAnswer.question_id == question_id)
    .first()
  )
  if existing_answer:
    existing_answer.answer = payload.answer
    existing_answer.teacher_id = current_user.id
    db.commit()
    db.refresh(existing_answer)
    return LessonAnswerRead.model_validate(existing_answer)

  answer = LessonAnswer(
    question_id=question_id,
    teacher_id=current_user.id,
    answer=payload.answer,
  )
  db.add(answer)
  db.commit()
  db.refresh(answer)
  return LessonAnswerRead.model_validate(answer)


@router.get("/students/{student_id}/report", response_model=StudentReport)
def get_student_report(
  student_id: int,
  current_user: User = Depends(require_role("teacher")),
  db: Session = Depends(get_db),
) -> StudentReport:
  course_ids = _get_teacher_course_ids(db, current_user.id)
  subject_ids = _get_teacher_subject_ids(db, current_user.id, course_ids)
  if not course_ids:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No courses found for teacher")

  student = db.query(User).filter(User.id == student_id, User.role == "student").first()
  if not student:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

  _ensure_student_in_courses(db, student_id, course_ids)

  progress_query = (
    db.query(ClassProgress)
    .filter(
      ClassProgress.student_id == student_id,
      ClassProgress.subject_id.in_(subject_ids) if subject_ids else True,
    )
  )

  progress_entries: List[StudentProgressEntry] = []
  for progress in progress_query.all():
    session = db.query(LegacySession).filter(LegacySession.id == progress.session_id).first()
    subject = db.query(Subject).filter(Subject.id == progress.subject_id).first()
    progress_entries.append(
      StudentProgressEntry(
        session_id=progress.session_id,
        session_title=session.title if session else "Session",
        subject_name=subject.name if subject else "Subject",
        completed=progress.completed,
        score=progress.score,
        completed_at=progress.completed_at,
      )
    )

  exam_results = (
    db.query(ExamResult)
    .join(Exam, Exam.id == ExamResult.exam_id)
    .filter(
      Exam.teacher_id == current_user.id,
      ExamResult.student_id == student_id,
    )
    .all()
  )

  return StudentReport(
    student_id=student.id,
    student_email=student.email,
    student_name=student.full_name,
    progress=progress_entries,
    exams=[ExamResultRead.model_validate(result) for result in exam_results],
  )
