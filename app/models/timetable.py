from sqlalchemy import Column, Integer, String, Time, Boolean, DateTime, func, ForeignKey, Enum
from app.models.base import Base

class Timetable(Base):
    __tablename__ = "timetables"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    week_day = Column(Enum("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", name="week_day"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())