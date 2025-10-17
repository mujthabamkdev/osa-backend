from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean
from app.models.base import Base

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    active_class_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)  # Current active class
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)