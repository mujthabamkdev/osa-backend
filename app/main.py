from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.routes import auth, users, courses, parents, students, admin, school, subjects, lessons, class_sessions, teachers


def _get_allowed_origins() -> list[str]:
  """Return CORS origins from env or fallback to common dev hosts."""
  if hasattr(settings, "CORS_ORIGINS") and settings.CORS_ORIGINS:
    # settings.CORS_ORIGINS can be str or list depending on .env usage
    if isinstance(settings.CORS_ORIGINS, str):
      return [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
    return list(settings.CORS_ORIGINS)

  return [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://0.0.0.0:4200",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.100.198:4200",
    "http://192.168.100.198:3000",
    "https://app.sevalla.com",
    "https://*.sevalla.com",
  ]


# Import models to register them with SQLAlchemy
from app.models.user import User
from app.models.course import Course
from app.models.class_model import Class
from app.models.subject import Subject
from app.models.lesson import Lesson
from app.models.timetable import Timetable
from app.models.session import Session, ClassSession
from app.models.session_content import SessionContent
from app.models.class_progress import ClassProgress
from app.models.enrollment import Enrollment
from app.models.live_class import LiveClass
from app.models.note import Note
from app.models.chapter import Chapter, Attachment, Quiz, QuizQuestion, LessonProgress
from app.models.exam import Exam
from app.models.exam_result import ExamResult
from app.models.lesson_question import LessonQuestion
from app.models.lesson_answer import LessonAnswer
from app.models.platform_setting import PlatformSetting

# Create all tables and ensure legacy SQLite databases gain new lesson ordering support
Base.metadata.create_all(bind=engine)


def _ensure_lessons_order_column() -> None:
  """Backfill the lessons.order_in_subject column when older SQLite DBs are reused."""
  if engine.url.get_backend_name() != "sqlite":
    return

  with engine.connect() as connection:
    columns = {
      row[1]
      for row in connection.execute(text("PRAGMA table_info(lessons)"))
    }
    if "order_in_subject" in columns:
      return

    connection.execute(
      text(
        "ALTER TABLE lessons ADD COLUMN order_in_subject INTEGER NOT NULL DEFAULT 1"
      )
    )
    connection.commit()


_ensure_lessons_order_column()

app = FastAPI(
  title="OSA Backend API",
  description="Online Sharia Academy Backend",
  version="1.0.0"
)

# CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=_get_allowed_origins(),  # ensure dev hosts like 127.0.0.1 are accepted
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["Courses"])
app.include_router(subjects.router, prefix="/api/v1", tags=["Subjects"])
app.include_router(lessons.router, prefix="/api/v1", tags=["Lessons"])
app.include_router(class_sessions.router, prefix="/api/v1", tags=["Class Sessions"])
app.include_router(school.router, prefix="/api/v1/school", tags=["School"])
app.include_router(parents.router, prefix="/api/v1/parents", tags=["Parents"])
app.include_router(students.router, prefix="/api/v1/students", tags=["Students"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(teachers.router, prefix="/api/v1/teachers", tags=["Teachers"])


@app.get("/")
def read_root():
  return {"message": "OSA Backend API", "version": "1.0.0"}


@app.get("/health")
def health_check():
  return {"status": "healthy"}