from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from app.models.base import Base


class LessonContent(Base):
  """
  Represents content for a lesson (video, notes, quiz).
  Examples: Video recording, Notes document, Quiz questions.
  
  Each lesson can have multiple content items.
  """

  __tablename__ = "lesson_content"

  id = Column(Integer, primary_key=True, index=True)
  lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
  content_type = Column(String(50), nullable=False)  # 'video', 'notes', 'quiz'
  title = Column(String(255), nullable=False)
  content_url = Column(String(500), nullable=True)
  content_text = Column(Text, nullable=True)
  order_in_lesson = Column(Integer, nullable=False, default=1)
  created_at = Column(DateTime, default=datetime.utcnow)

  # Relationships will be configured after all models are imported