from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text

from app.models.base import Base


class Lesson(Base):
  """
  Represents a lesson within a course, scheduled on a specific date.
  Examples: "Introduction to Quran", "Hadith Basics", etc.
  
  Lessons belong to courses and are categorized by subjects.
  Each lesson can have multiple content items (video, notes, quiz).
  """

  __tablename__ = "lessons"

  id = Column(Integer, primary_key=True, index=True)
  course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
  subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
  title = Column(String(255), nullable=False)
  description = Column(Text, nullable=True)
  scheduled_date = Column(Date, nullable=True)
  order_in_subject = Column(Integer, nullable=False, default=1)
  created_at = Column(DateTime, default=datetime.utcnow)

  # Relationships will be configured after all models are imported
