#!/usr/bin/env python3
import sys
import os
from datetime import datetime, timedelta, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.live_class import LiveClass
from app.models.chapter import Chapter
from app.models.course import Course
from app.models.user import User

def create_class_one_schedule():
    db = SessionLocal()

    try:
        # Get the course
        course = db.query(Course).filter(Course.id == 1).first()
        if not course:
            print("Course with ID 1 not found.")
            return

        # Get a teacher
        teacher = db.query(User).filter(User.role == "teacher").first()
        if not teacher:
            print("No teacher found.")
            return

        # Get all chapters for class one subjects
        chapters = db.query(Chapter).filter(
            Chapter.course_id == course.id,
            Chapter.title.like("Class One - %")
        ).all()

        # Create chapter mapping
        chapter_map = {}
        for chapter in chapters:
            subject_name = chapter.title.replace("Class One - ", "")
            chapter_map[subject_name] = chapter

        print(f"Found {len(chapter_map)} subject chapters")

        # Define the 5-day schedule (same as generated before)
        schedule = [
            {"day": 1, "subjects": ["Nahv", "Hadees"]},
            {"day": 2, "subjects": ["Quran", "Nahv"]},
            {"day": 3, "subjects": ["Hadees", "Nahv"]},
            {"day": 4, "subjects": ["Nahv", "Swarf"]},
            {"day": 5, "subjects": ["Fiqh", "Hadees"]}
        ]

        # Create live classes starting from tomorrow
        base_date = datetime.now() + timedelta(days=1)  # Start from tomorrow
        created_classes = 0

        print("\nCreating live classes schedule:")
        print("=" * 50)

        for day_info in schedule:
            day_date = base_date + timedelta(days=day_info['day'] - 1)

            # First subject: 9:00 AM - 9:40 AM
            subject1 = day_info['subjects'][0]
            if subject1 in chapter_map:
                live_class1 = LiveClass(
                    course_id=course.id,
                    chapter_id=chapter_map[subject1].id,
                    title=f"Class One - {subject1} (Live Session)",
                    description=f"Live class session for {subject1}",
                    scheduled_date=day_date,
                    start_time=time(9, 0),  # 9:00 AM
                    end_time=time(9, 40),    # 9:40 AM
                    meeting_link="https://meet.google.com/example-class-one",
                    teacher_id=teacher.id,
                    is_active=True
                )
                db.add(live_class1)
                print(f"Day {day_info['day']} - {subject1}: {day_date.strftime('%Y-%m-%d')} 9:00-9:40 AM")
                created_classes += 1

            # Second subject: 10:00 AM - 10:40 AM
            subject2 = day_info['subjects'][1]
            if subject2 in chapter_map:
                live_class2 = LiveClass(
                    course_id=course.id,
                    chapter_id=chapter_map[subject2].id,
                    title=f"Class One - {subject2} (Live Session)",
                    description=f"Live class session for {subject2}",
                    scheduled_date=day_date,
                    start_time=time(10, 0),  # 10:00 AM
                    end_time=time(10, 40),   # 10:40 AM
                    meeting_link="https://meet.google.com/example-class-one",
                    teacher_id=teacher.id,
                    is_active=True
                )
                db.add(live_class2)
                print(f"Day {day_info['day']} - {subject2}: {day_date.strftime('%Y-%m-%d')} 10:00-10:40 AM")
                created_classes += 1

        db.commit()

        print(f"\nSuccessfully created {created_classes} live class sessions!")
        print("Schedule Summary:")
        print("- 2 subjects per day (40 minutes each)")
        print("- Days 1-5 starting from tomorrow")
        print("- Subject 1: 9:00 AM - 9:40 AM")
        print("- Subject 2: 10:00 AM - 10:40 AM")

    except Exception as e:
        print(f"Error creating schedule: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_class_one_schedule()