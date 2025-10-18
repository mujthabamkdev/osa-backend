from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  email = Column(String, unique=True, index=True, nullable=False)
  hashed_password = Column(String, nullable=False)
  full_name = Column(String, nullable=True)
  role = Column(String, nullable=False, default="student")  # student, teacher, admin, parent
  is_active = Column(Boolean, default=True)
  created_at = Column(DateTime, default=datetime.utcnow)

  # Relationships - using viewonly to avoid FK issues during import
  # These will be configured after all models are imported