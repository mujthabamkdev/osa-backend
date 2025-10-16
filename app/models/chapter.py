from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean
from app.models.base import Base

class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # video, document, audio, etc.
    source = Column(String(50), nullable=False, default="upload")  # upload or youtube
    file_size = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    passing_score = Column(Integer, nullable=False, default=70)  # percentage
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON string of options
    correct_answer = Column(Integer, nullable=False)  # index of correct option
    order = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    quiz_score = Column(Integer, nullable=True)  # percentage score
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())