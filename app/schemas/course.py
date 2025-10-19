from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class SubjectBase(BaseModel):
  name: str
  description: str = ""
  instructor_id: Optional[int] = None
  order_in_course: int = 1


class SubjectRead(SubjectBase):
  id: int
  course_id: int

  class Config:
    from_attributes = True


class LessonBase(BaseModel):
  title: str
  description: Optional[str] = None
  scheduled_date: date = Field(default_factory=date.today)
  order_in_subject: int = 1


class LessonRead(LessonBase):
  id: int
  subject_id: int

  class Config:
    from_attributes = True


class LessonUpdate(BaseModel):
  title: Optional[str] = None
  description: Optional[str] = None
  scheduled_date: Optional[date] = None
  order_in_subject: Optional[int] = None


class ClassSessionBase(BaseModel):
  session_date: str  # YYYY-MM-DD format
  start_time: str  # HH:MM:SS format
  end_time: str  # HH:MM:SS format
  is_completed: bool = False


class ClassSessionRead(ClassSessionBase):
  id: int
  lesson_id: int

  class Config:
    from_attributes = True


# Nested schemas for hierarchical responses
class LessonWithSessions(LessonRead):
  class_sessions: List[ClassSessionRead] = []


class SubjectWithLessons(SubjectRead):
  lessons: List[LessonWithSessions] = []


class CourseBase(BaseModel):
  title: str
  description: str = ""


class CourseCreate(CourseBase):
  teacher_id: int


class CourseRead(CourseBase):
  id: int
  teacher_id: int

  class Config:
    from_attributes = True


class CourseWithSubjects(CourseRead):
  subjects: List[SubjectWithLessons] = []


class SubjectCreate(SubjectBase):
  course_id: int


class LessonCreate(LessonBase):
  subject_id: int
  course_id: Optional[int] = None


class LessonContentBase(BaseModel):
  lesson_id: int
  title: str
  content_type: str
  content_url: Optional[str] = None
  content_text: Optional[str] = None
  order_in_lesson: int = 1


class LessonContentCreate(LessonContentBase):
  pass


class LessonContentUpdate(BaseModel):
  title: Optional[str] = None
  content_type: Optional[str] = None
  content_url: Optional[str] = None
  content_text: Optional[str] = None
  order_in_lesson: Optional[int] = None


class LessonContentRead(LessonContentBase):
  id: int

  class Config:
    from_attributes = True


class ClassSessionCreate(ClassSessionBase):
  lesson_id: int