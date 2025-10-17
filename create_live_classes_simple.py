#!/usr/bin/env python3
import sys
import os
from datetime import datetime, timedelta, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

def create_live_classes_sql():
    db = SessionLocal()

    try:
        # Define the schedule
        schedule = [
            {"day": 1, "subjects": ["Nahv", "Hadees"]},
            {"day": 2, "subjects": ["Quran", "Nahv"]},
            {"day": 3, "subjects": ["Hadees", "Nahv"]},
            {"day": 4, "subjects": ["Nahv", "Swarf"]},
            {"day": 5, "subjects": ["Fiqh", "Hadees"]}
        ]

        # Get chapter mappings
        chapters = {}
        result = db.execute(text("SELECT id, title FROM chapters WHERE title LIKE 'Class One - %'"))
        for row in result:
            subject_name = row[1].replace("Class One - ", "")
            chapters[subject_name] = row[0]

        print(f"Found chapters: {chapters}")

        # Create live classes starting from tomorrow
        base_date = datetime.now() + timedelta(days=1)
        created_classes = 0

        print("\nCreating live classes with raw SQL:")

        for day_info in schedule:
            day_date = base_date + timedelta(days=day_info['day'] - 1)
            date_str = day_date.strftime('%Y-%m-%d')

            # First subject: 9:00 AM - 9:40 AM
            subject1 = day_info['subjects'][0]
            if subject1 in chapters:
                db.execute(text("""
                    INSERT INTO live_classes (course_id, chapter_id, title, description, scheduled_date, start_time, end_time, meeting_link, teacher_id, is_active, created_at)
                    VALUES (:course_id, :chapter_id, :title, :description, :scheduled_date, :start_time, :end_time, :meeting_link, :teacher_id, :is_active, :created_at)
                """), {
                    'course_id': 1,
                    'chapter_id': chapters[subject1],
                    'title': f"Class One - {subject1} (Live Session)",
                    'description': f"Live class session for {subject1}",
                    'scheduled_date': day_date,
                    'start_time': '09:00:00',
                    'end_time': '09:40:00',
                    'meeting_link': "https://meet.google.com/example-class-one",
                    'teacher_id': 2,
                    'is_active': True,
                    'created_at': datetime.utcnow()
                })
                print(f"Day {day_info['day']} - {subject1}: {date_str} 9:00-9:40 AM")
                created_classes += 1

            # Second subject: 10:00 AM - 10:40 AM
            subject2 = day_info['subjects'][1]
            if subject2 in chapters:
                db.execute(text("""
                    INSERT INTO live_classes (course_id, chapter_id, title, description, scheduled_date, start_time, end_time, meeting_link, teacher_id, is_active, created_at)
                    VALUES (:course_id, :chapter_id, :title, :description, :scheduled_date, :start_time, :end_time, :meeting_link, :teacher_id, :is_active, :created_at)
                """), {
                    'course_id': 1,
                    'chapter_id': chapters[subject2],
                    'title': f"Class One - {subject2} (Live Session)",
                    'description': f"Live class session for {subject2}",
                    'scheduled_date': day_date,
                    'start_time': '10:00:00',
                    'end_time': '10:40:00',
                    'meeting_link': "https://meet.google.com/example-class-one",
                    'teacher_id': 2,
                    'is_active': True,
                    'created_at': datetime.utcnow()
                })
                print(f"Day {day_info['day']} - {subject2}: {date_str} 10:00-10:40 AM")
                created_classes += 1

        db.commit()

        print(f"\nSuccessfully created {created_classes} live class sessions!")

        # Verify the classes were created
        result = db.execute(text("SELECT COUNT(*) FROM live_classes"))
        count = result.fetchone()[0]
        print(f"Total live classes in database: {count}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_live_classes_sql()