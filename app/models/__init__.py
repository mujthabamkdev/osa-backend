from .base import Base
from .user import User
from .course import Course
from .class_model import Class
from .subject import Subject
from .lesson import Lesson
from .lesson_content import LessonContent
from .timetable import Timetable
from .session import Session, ClassSession
from .session_content import SessionContent
from .class_progress import ClassProgress
from .enrollment import Enrollment
from .note import Note
from .live_class import LiveClass
from .chapter import Chapter, Attachment

# Configure deferred relationships after all models are imported
# Temporarily disabled to avoid mapper initialization issues
# from sqlalchemy.orm import relationship

# Add relationships to User that were deferred
# User.courses = relationship("Course", back_populates="teacher", lazy="select")
# User.subjects = relationship("Subject", back_populates="instructor", lazy="select")

# Add relationships to Course that were deferred
# Course.subjects = relationship("Subject", back_populates="course", cascade="all, delete-orphan", lazy="select")
# Course.teacher = relationship("User", back_populates="courses", lazy="select")

# Add relationships to Subject that were deferred
# Subject.course = relationship("Course", back_populates="subjects", lazy="select")
# Subject.lessons = relationship("Lesson", back_populates="subject", cascade="all, delete-orphan", lazy="select")
# Subject.instructor = relationship("User", back_populates="subjects", lazy="select")

__all__ = [
  "Base",
  "User",
  "Course",
  "Class",
  "Subject",
  "Lesson",
  "LessonContent",
  "Timetable",
  "Session",
  "ClassSession",
  "SessionContent",
  "ClassProgress",
  "Enrollment",
  "Note",
  "LiveClass",
  "Chapter",
  "Attachment",
]