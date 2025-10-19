from sqlalchemy import Column, Integer, Text, DateTime, func, ForeignKey, Boolean

from app.models.base import Base


class LessonQuestion(Base):
  __tablename__ = "lesson_questions"

  id = Column(Integer, primary_key=True, index=True)
  lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
  student_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
  question = Column(Text, nullable=False)
  is_anonymous = Column(Boolean, nullable=False, default=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
