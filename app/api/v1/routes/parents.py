from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User

router = APIRouter()

# Mock child data structure - in a real app this would come from a proper relationship
class ChildResponse:
    def __init__(self, id: int, name: str, email: str, grade: str = "N/A", enrolled_courses: int = 0, average_progress: int = 0, last_active: str = "Never"):
        self.id = id
        self.name = name
        self.email = email
        self.grade = grade
        self.enrolledCourses = enrolled_courses
        self.averageProgress = average_progress
        self.lastActive = last_active

@router.get("/{parent_id}/children", response_model=List[dict])
def get_parent_children(parent_id: int, db: Session = Depends(get_db)):
    """
    Get children associated with a parent.
    Currently returns mock data since parent-child relationships are not implemented.
    """
    # Verify parent exists and has parent role
    parent = db.query(User).filter(User.id == parent_id, User.role == "parent").first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    # TODO: Implement actual parent-child relationship
    # For now, return empty list since no relationship exists
    return []