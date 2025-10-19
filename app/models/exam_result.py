from sqlalchemy import Column, Integer, Text, DateTime, func, ForeignKey, String

from app.models.base import Base


class ExamResult(Base):
  __tablename__ = "exam_results"

  id = Column(Integer, primary_key=True, index=True)
  exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, index=True)
  student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
  score = Column(Integer, nullable=False)
  max_score = Column(Integer, nullable=True)
  status = Column(String(50), nullable=True)
  feedback = Column(Text, nullable=True)
  published_at = Column(DateTime(timezone=True), nullable=True)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), onupdate=func.now())
