from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from app.models.base import Base


class Subject(Base):
  """
  Represents a subject within a course.
  Examples: Quran, Hadith, Fiqh, Aqeedah, Arabic, Islamic History
  
  Subjects belong to courses and are used to categorize lessons.
  """

  __tablename__ = "subjects"

  id = Column(Integer, primary_key=True, index=True)
  course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
  name = Column(String(255), nullable=False)
  description = Column(Text, nullable=False, server_default="")
  instructor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
  order_in_course = Column(Integer, nullable=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())

  # Relationships will be configured after all models are imported