from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func, ForeignKey, Enum
from app.models.base import Base


class SessionContent(Base):
  """
  Represents content within a class session.
  Can be a video, note, quiz, or assignment.
  """

  __tablename__ = "session_contents"

  id = Column(Integer, primary_key=True, index=True)
  class_session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=False)
  title = Column(String(255), nullable=False)
  description = Column(Text, nullable=False, server_default="")
  content_type = Column(
    Enum("video", "note", "quiz", "assignment", name="content_type"),
    nullable=False
  )
  content_url = Column(String(500), nullable=True)
  content_text = Column(Text, nullable=True)
  order = Column(Integer, nullable=False)
  duration = Column(Integer, nullable=True)  # in minutes
  is_required = Column(Boolean, nullable=False, default=True)
  created_at = Column(DateTime(timezone=True), server_default=func.now())

  # Relationships will be configured after all models are imported