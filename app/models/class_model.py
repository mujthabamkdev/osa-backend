from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Class(Base):
  """
  DEPRECATED - Kept for backwards compatibility during migration.
  This model represented a year-based class (Class 1-5 for different levels).
  
  The new hierarchy uses:
  - Course → Subject → Lesson → ClassSession
  - This Class model is replaced by the Lesson model.
  """

  __tablename__ = "classes"

  id = Column(Integer, primary_key=True, index=True)
  course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
  year = Column(Integer, nullable=False)  # 1-5 for Class 1, Class 2, etc.
  name = Column(String(255), nullable=False)
  is_active = Column(Boolean, nullable=False, default=True)
  created_at = Column(DateTime(timezone=True), server_default=func.now())