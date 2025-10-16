from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Time, Boolean
from app.models.base import Base

class LiveClass(Base):
    __tablename__ = "live_classes"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    meeting_link = Column(String(500), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())