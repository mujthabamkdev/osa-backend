from datetime import datetime, time
from typing import Optional, List

from pydantic import BaseModel, Field


class TeacherStudent(BaseModel):
  id: int
  email: str
  full_name: Optional[str]
  course_id: int
  course_title: str


class TeacherSubject(BaseModel):
  id: int
  name: str
  course_id: int
  course_title: str


class TeacherOverview(BaseModel):
  total_students: int = 0
  total_subjects: int = 0
  total_courses: int = 0
  upcoming_live_classes: int = 0
  pending_questions: int = 0


class ExamBase(BaseModel):
  title: str
  course_id: int
  subject_id: Optional[int] = None
  description: str = ""
  scheduled_date: Optional[datetime] = None
  duration_minutes: Optional[int] = Field(default=None, ge=0)
  max_score: Optional[int] = Field(default=None, ge=0)


class ExamCreate(ExamBase):
  pass


class ExamRead(ExamBase):
  id: int
  teacher_id: int
  is_published: bool
  created_at: datetime

  class Config:
    from_attributes = True


class ExamResultBase(BaseModel):
  student_id: int
  score: int = Field(ge=0)
  max_score: Optional[int] = Field(default=None, ge=0)
  status: Optional[str] = None
  feedback: Optional[str] = None
  published_at: Optional[datetime] = None


class ExamResultCreate(ExamResultBase):
  pass


class ExamResultRead(ExamResultBase):
  id: int
  exam_id: int
  created_at: datetime

  class Config:
    from_attributes = True


class ExamResultBulkCreate(BaseModel):
  results: List[ExamResultCreate]


class LessonQuestionCreate(BaseModel):
  question: str
  is_anonymous: bool = False


class LessonQuestionRead(BaseModel):
  id: int
  lesson_id: int
  question: str
  student_id: Optional[int]
  is_anonymous: bool
  created_at: datetime
  answer: Optional[str] = None
  answered_by: Optional[int] = None
  answered_at: Optional[datetime] = None


class LessonAnswerCreate(BaseModel):
  answer: str


class LessonAnswerRead(BaseModel):
  id: int
  question_id: int
  teacher_id: int
  answer: str
  created_at: datetime

  class Config:
    from_attributes = True


class LiveClassCreate(BaseModel):
  course_id: int
  title: str
  description: str = ""
  scheduled_date: datetime
  start_time: time
  end_time: time
  meeting_link: Optional[str] = None
  chapter_id: Optional[int] = None


class LiveClassRead(BaseModel):
  id: int
  course_id: int
  teacher_id: int
  title: str
  description: str
  scheduled_date: datetime
  start_time: time
  end_time: time
  meeting_link: Optional[str]
  chapter_id: Optional[int]
  is_active: bool
  created_at: datetime

  class Config:
    from_attributes = True


class StudentProgressEntry(BaseModel):
  session_id: int
  session_title: str
  subject_name: str
  completed: bool
  score: Optional[int]
  completed_at: Optional[datetime]


class StudentReport(BaseModel):
  student_id: int
  student_email: str
  student_name: Optional[str]
  progress: List[StudentProgressEntry]
  exams: List[ExamResultRead] = []
