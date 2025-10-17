#!/usr/bin/env python3
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.chapter import Chapter, Attachment
from app.models.course import Course
from app.models.user import User
from datetime import datetime, timedelta

# Subject data with YouTube video links (40-minute lessons)
SUBJECTS = {
    "Swarf": {
        "description": "Study of Islamic Jurisprudence and Law",
        "videos": [
            {
                "title": "Introduction to Swarf - Part 1",
                "url": "https://www.youtube.com/watch?v=example_swarf1",
                "duration": 2400  # 40 minutes in seconds
            },
            {
                "title": "Introduction to Swarf - Part 2",
                "url": "https://www.youtube.com/watch?v=example_swarf2",
                "duration": 2400
            },
            {
                "title": "Sources of Islamic Law",
                "url": "https://www.youtube.com/watch?v=example_swarf3",
                "duration": 2400
            }
        ]
    },
    "Nahv": {
        "description": "Arabic Grammar and Syntax",
        "videos": [
            {
                "title": "Arabic Grammar Basics - Part 1",
                "url": "https://www.youtube.com/watch?v=example_nahv1",
                "duration": 2400
            },
            {
                "title": "Arabic Grammar Basics - Part 2",
                "url": "https://www.youtube.com/watch?v=example_nahv2",
                "duration": 2400
            },
            {
                "title": "Sentence Structure in Arabic",
                "url": "https://www.youtube.com/watch?v=example_nahv3",
                "duration": 2400
            }
        ]
    },
    "Fiqh": {
        "description": "Islamic Jurisprudence and Practice",
        "videos": [
            {
                "title": "Understanding Fiqh - Part 1",
                "url": "https://www.youtube.com/watch?v=example_fiqh1",
                "duration": 2400
            },
            {
                "title": "Understanding Fiqh - Part 2",
                "url": "https://www.youtube.com/watch?v=example_fiqh2",
                "duration": 2400
            },
            {
                "title": "Practical Applications of Fiqh",
                "url": "https://www.youtube.com/watch?v=example_fiqh3",
                "duration": 2400
            }
        ]
    },
    "Quran": {
        "description": "Study of the Holy Quran",
        "videos": [
            {
                "title": "Quran Recitation Basics - Part 1",
                "url": "https://www.youtube.com/watch?v=example_quran1",
                "duration": 2400
            },
            {
                "title": "Quran Recitation Basics - Part 2",
                "url": "https://www.youtube.com/watch?v=example_quran2",
                "duration": 2400
            },
            {
                "title": "Understanding Quranic Verses",
                "url": "https://www.youtube.com/watch?v=example_quran3",
                "duration": 2400
            }
        ]
    },
    "Hadees": {
        "description": "Study of Prophet Muhammad's Traditions",
        "videos": [
            {
                "title": "Introduction to Hadees - Part 1",
                "url": "https://www.youtube.com/watch?v=example_hadees1",
                "duration": 2400
            },
            {
                "title": "Introduction to Hadees - Part 2",
                "url": "https://www.youtube.com/watch?v=example_hadees2",
                "duration": 2400
            },
            {
                "title": "Authenticity of Hadees",
                "url": "https://www.youtube.com/watch?v=example_hadees3",
                "duration": 2400
            }
        ]
    }
}

def create_class_one_subjects():
    db = SessionLocal()

    try:
        # Get the existing course (Online Sharia)
        course = db.query(Course).filter(Course.id == 1).first()
        if not course:
            print("Course with ID 1 not found. Please create a course first.")
            return

        # Get a teacher (assuming there's at least one teacher)
        teacher = db.query(User).filter(User.role == "teacher").first()
        if not teacher:
            print("No teacher found. Please create a teacher user first.")
            return

        print(f"Adding subjects to course: {course.title}")

        # Create chapters for each subject
        chapter_order = 1
        created_chapters = []

        for subject_name, subject_data in SUBJECTS.items():
            chapter = Chapter(
                course_id=course.id,
                title=f"Class One - {subject_name}",
                description=subject_data["description"],
                order=chapter_order
            )
            db.add(chapter)
            created_chapters.append((chapter, subject_data))
            chapter_order += 1

        db.commit()
        print(f"Created {len(created_chapters)} subject chapters")

        # Create video attachments for each chapter
        total_attachments = 0
        for chapter, subject_data in created_chapters:
            for video in subject_data["videos"]:
                attachment = Attachment(
                    course_id=course.id,
                    chapter_id=chapter.id,
                    title=video["title"],
                    description=f"40-minute video lesson for {chapter.title}",
                    file_url=video["url"],
                    file_type="video",
                    source="youtube",
                    duration=video["duration"],
                    uploaded_at=datetime.utcnow()
                )
                db.add(attachment)
                total_attachments += 1

        db.commit()
        print(f"Created {total_attachments} video attachments")

        # Create a random schedule: 2 subjects per day for 5 days
        print("\nCreating random 5-day schedule (2 subjects per day):")
        subject_names = list(SUBJECTS.keys())
        schedule = []

        # Create 5 days of schedule
        for day in range(1, 6):
            # Randomly select 2 subjects for the day
            daily_subjects = random.sample(subject_names, 2)
            schedule.append({
                "day": day,
                "subjects": daily_subjects
            })

        # Print the schedule
        print("\nClass One Daily Schedule:")
        print("=" * 40)
        for day_info in schedule:
            subject1 = day_info['subjects'][0]
            subject2 = day_info['subjects'][1]
            print(f"Day {day_info['day']}: {subject1} + {subject2}")

        print("\nClass One subjects and schedule created successfully!")
        print(f"Total chapters: {len(created_chapters)}")
        print(f"Total video lessons: {total_attachments}")

    except Exception as e:
        print(f"Error creating class one subjects: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_class_one_subjects()