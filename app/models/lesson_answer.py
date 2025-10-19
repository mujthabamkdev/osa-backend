from sqlalchemy import Column, Integer, Text, DateTime, func, ForeignKey

from app.models.base import Base


class LessonAnswer(Base):
  __tablename__ = "lesson_answers"

  id = Column(Integer, primary_key=True, index=True)
  question_id = Column(Integer, ForeignKey("lesson_questions.id"), nullable=False, index=True)
  teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
  answer = Column(Text, nullable=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
