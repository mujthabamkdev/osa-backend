from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class ClassBase(BaseModel):
    course_id: int
    year: int
    name: str
    is_active: Optional[bool] = True

class ClassCreate(ClassBase):
    pass

class ClassRead(ClassBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SubjectBase(BaseModel):
    class_id: int
    name: str
    description: Optional[str] = ""
    instructor_id: Optional[int] = None
    order_in_class: int

class SubjectCreate(SubjectBase):
    pass

class SubjectRead(SubjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TimetableBase(BaseModel):
    class_id: int
    subject_id: int
    week_day: str  # monday, tuesday, etc.
    start_time: time
    end_time: time
    is_active: Optional[bool] = True

class TimetableCreate(TimetableBase):
    pass

class TimetableRead(TimetableBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    subject_id: int
    title: str
    description: Optional[str] = ""
    session_date: date
    start_time: time
    end_time: time
    is_completed: Optional[bool] = False

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SessionContentBase(BaseModel):
    session_id: int
    title: str
    description: Optional[str] = ""
    content_type: str  # video, note, quiz, assignment
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    order: int
    duration: Optional[int] = None
    is_required: Optional[bool] = True

class SessionContentCreate(SessionContentBase):
    pass

class SessionContentRead(SessionContentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ClassProgressBase(BaseModel):
    student_id: int
    class_id: int
    subject_id: int
    session_id: int
    completed: Optional[bool] = False
    score: Optional[int] = None

class ClassProgressCreate(ClassProgressBase):
    pass

class ClassProgressRead(ClassProgressBase):
    id: int
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True