"""
Seed script to populate the database with the new course structure.

New hierarchy:
- Course: Online Sharia
  - Subject: Fiqh (5 lessons)
  - Subject: Quran (3 lessons)
  - Subject: Nahv (2 lessons)
  - Subject: Sarf (2 lessons)
  - Subject: Hadees (2 lessons)

Each lesson has multiple class sessions scheduled on different days.
"""

from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models import (
  User,
  Course,
  Subject,
  Lesson,
  ClassSession,
  Chapter,
  Attachment,
)
from app.core.security import get_password_hash


def create_seed_data():
  """Create sample data for the new course structure."""
  db = SessionLocal()

  try:
    # Clear existing data (be careful with this in production!)
    # db.query(ClassSession).delete()
    # db.query(Lesson).delete()
    # db.query(Subject).delete()
    # db.query(Course).delete()
    # db.query(User).delete()
    # db.commit()

    # 1. Create users
    teacher = User(
      email="teacher@example.com",
      hashed_password=get_password_hash("password123"),
      full_name="Dr. Ahmed Al-Kareem",
      role="teacher",
      is_active=True
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    instructors = []
    subjects_list = ["Fiqh", "Quran", "Nahv", "Sarf", "Hadees"]
    for i, subject_name in enumerate(subjects_list):
      instructor = User(
        email=f"instructor_{subject_name.lower()}@example.com",
        hashed_password=get_password_hash("password123"),
        full_name=f"Sh. {subject_name} Expert",
        role="teacher",
        is_active=True
      )
      db.add(instructor)
      instructors.append(instructor)

    db.commit()

    # 2. Create course
    course = Course(
      title="Online Sharia",
      description="Comprehensive Islamic Studies Program",
      teacher_id=teacher.id
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    # 3. Create subjects with lessons
    start_date = date.today()
    session_date = start_date

    subjects_config = {
      "Fiqh": 5,
      "Quran": 3,
      "Nahv": 2,
      "Sarf": 2,
      "Hadees": 2,
    }

    for subject_order, (subject_name, num_lessons) in enumerate(subjects_config.items()):
      instructor = instructors[subject_order]

      subject = Subject(
        course_id=course.id,
        name=subject_name,
        description=f"{subject_name} - Islamic studies subject",
        instructor_id=instructor.id,
        order_in_course=subject_order + 1
      )
      db.add(subject)
      db.commit()
      db.refresh(subject)

      # Create lessons for each subject
      for lesson_num in range(1, num_lessons + 1):
        lesson = Lesson(
          subject_id=subject.id,
          title=f"Class {lesson_num}",
          description=f"{subject_name} - Lesson {lesson_num}",
          order_in_subject=lesson_num
        )
        db.add(lesson)
        db.commit()
        db.refresh(lesson)

        # Create class sessions for each lesson (3 sessions per lesson on different days)
        for session_num in range(3):
          session_day = session_date + timedelta(days=session_num * 7)
          
          class_session = ClassSession(
            lesson_id=lesson.id,
            session_date=session_day,
            start_time=time(14, 0),  # 2:00 PM
            end_time=time(15, 0),  # 3:00 PM
            is_completed=False
          )
          db.add(class_session)

        db.commit()

        # Create sample chapter
        chapter = Chapter(
          lesson_id=lesson.id,
          title=f"{subject_name} - Chapter 1",
          description="Introduction chapter",
          order=1
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)

        # Create sample attachment
        attachment = Attachment(
          course_id=course.id,
          lesson_id=lesson.id,
          title=f"{subject_name} Video",
          description="Sample video content",
          file_url="https://example.com/video.mp4",
          file_type="video",
          source="youtube",
          duration=3600  # 1 hour in seconds
        )
        db.add(attachment)

      db.commit()
      session_date = session_date + timedelta(days=7 * num_lessons)

    print("✅ Seed data created successfully!")
    print(f"✅ Course: {course.title}")
    print(f"✅ Subjects: {len(subjects_config)}")
    total_lessons = sum(subjects_config.values())
    print(f"✅ Total Lessons: {total_lessons}")
    print(f"✅ Total Class Sessions: {total_lessons * 3}")

  except Exception as e:
    db.rollback()
    print(f"❌ Error creating seed data: {e}")
    raise
  finally:
    db.close()


if __name__ == "__main__":
  # Ensure tables exist
  Base.metadata.create_all(bind=engine)
  create_seed_data()
