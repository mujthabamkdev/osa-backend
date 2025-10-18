from sqlalchemy import Column, Integer, Boolean, DateTime, func, ForeignKey
from app.models.base import Base

class ClassProgress(Base):
    __tablename__ = "class_progress"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    score = Column(Integer, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)