from pydantic import BaseModel

class CourseBase(BaseModel):
    title: str
    description: str = ""

class CourseCreate(CourseBase):
    teacher_id: int

class CourseRead(CourseBase):
    id: int
    teacher_id: int
class Config:
    from_attributes = True
