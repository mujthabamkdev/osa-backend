from pydantic import BaseModel
from typing import Optional, List


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
  order_in_subject: int = 1


class LessonRead(LessonBase):
  id: int
  subject_id: int

  class Config:
    from_attributes = True


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


class ClassSessionCreate(ClassSessionBase):
  lesson_id: int