from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint, func

from app.models.base import Base


class ParentStudent(Base):
    """Associates a parent account with the students they can access."""

    __tablename__ = "parent_students"
    __table_args__ = (UniqueConstraint("parent_id", "student_id", name="uq_parent_student"),)

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
