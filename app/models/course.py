from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from app.models.base import Base


class Course(Base):
  __tablename__ = "courses"
  id = Column(Integer, primary_key=True, index=True)
  title = Column(String(255), nullable=False)
  description = Column(Text, default="")
  teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())

  # Relationships will be configured after all models are imported