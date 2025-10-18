from sqlalchemy import Column, Integer, String, Text, Date, Time, Boolean, DateTime, func, ForeignKey
from app.models.base import Base


class Session(Base):
  """
  DEPRECATED: Use ClassSession instead.
  Kept for backwards compatibility during migration.
  """

  __tablename__ = "sessions"

  id = Column(Integer, primary_key=True, index=True)
  subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
  title = Column(String(255), nullable=False)
  description = Column(Text, nullable=False, server_default="")
  session_date = Column(Date, nullable=False)
  start_time = Column(Time, nullable=False)
  end_time = Column(Time, nullable=False)
  is_completed = Column(Boolean, nullable=False, default=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())


class ClassSession(Base):
  """
  Represents a scheduled instance of a lesson.
  Examples: Fiqh Class 1 on Day 1, Fiqh Class 1 on Day 8, etc.
  
  A lesson can have multiple class sessions scheduled on different days.
  This replaces the old Session model which was subject-based.
  """

  __tablename__ = "class_sessions"

  id = Column(Integer, primary_key=True, index=True)
  lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
  session_date = Column(Date, nullable=False)
  start_time = Column(Time, nullable=False)
  end_time = Column(Time, nullable=False)
  is_completed = Column(Boolean, nullable=False, default=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())

  # Relationships will be configured after all models are imported