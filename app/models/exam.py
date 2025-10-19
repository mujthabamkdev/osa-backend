from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean

from app.models.base import Base


class Exam(Base):
  __tablename__ = "exams"

  id = Column(Integer, primary_key=True, index=True)
  course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
  subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True, index=True)
  teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
  title = Column(String(255), nullable=False)
  description = Column(Text, nullable=False, default="")
  scheduled_date = Column(DateTime(timezone=True), nullable=True)
  duration_minutes = Column(Integer, nullable=True)
  max_score = Column(Integer, nullable=True)
  is_published = Column(Boolean, nullable=False, default=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
