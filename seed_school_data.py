#!/usr/bin/env python3
"""
Seed data script for the OSA school model.
Creates initial classes, subjects, and timetables.
"""

from app.core.database import engine
from app.models import Class, Subject, Timetable, Course
from sqlalchemy.orm import sessionmaker
from datetime import time

def seed_school_data():
    """Create seed data for the school model"""

    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Get the first course (assuming it exists)
        course = db.query(Course).first()
        if not course:
            print("No course found. Please create a course first.")
            return

        print(f"Seeding data for course: {course.title}")

        # Create classes for years 1-5
        classes_data = [
            {"year": 1, "name": "Class 1"},
            {"year": 2, "name": "Class 2"},
            {"year": 3, "name": "Class 3"},
            {"year": 4, "name": "Class 4"},
            {"year": 5, "name": "Class 5"},
        ]

        classes = []
        for class_data in classes_data:
            # Check if class already exists
            existing_class = db.query(Class).filter(
                Class.course_id == course.id,
                Class.year == class_data["year"]
            ).first()

            if existing_class:
                print(f"Class {class_data['name']} already exists")
                classes.append(existing_class)
            else:
                new_class = Class(
                    course_id=course.id,
                    year=class_data["year"],
                    name=class_data["name"],
                    is_active=True
                )
                db.add(new_class)
                classes.append(new_class)
                print(f"Created class: {class_data['name']}")

        db.commit()

        # Create subjects for each class
        subjects_data = [
            {"name": "Quran Studies", "description": "Study of the Holy Quran"},
            {"name": "Hadith Studies", "description": "Study of Prophet's traditions"},
            {"name": "Islamic Jurisprudence (Fiqh)", "description": "Islamic law and practice"},
            {"name": "Islamic Theology (Aqeedah)", "description": "Islamic beliefs and creed"},
            {"name": "Arabic Language", "description": "Arabic language learning"},
            {"name": "Islamic History", "description": "History of Islam and Muslims"},
        ]

        for i, class_obj in enumerate(classes):
            for j, subject_data in enumerate(subjects_data):
                # Check if subject already exists
                existing_subject = db.query(Subject).filter(
                    Subject.class_id == class_obj.id,
                    Subject.name == subject_data["name"]
                ).first()

                if existing_subject:
                    print(f"Subject {subject_data['name']} already exists for {class_obj.name}")
                else:
                    new_subject = Subject(
                        class_id=class_obj.id,
                        name=subject_data["name"],
                        description=subject_data["description"],
                        order_in_class=j + 1
                        # instructor_id will default to None
                    )
                    db.add(new_subject)
                    print(f"Created subject: {subject_data['name']} for {class_obj.name}")

        db.commit()

        print("Subjects created successfully! Skipping timetable creation for now.")
        # # Create basic timetable (Monday to Friday, 3 subjects per day)
        # week_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        # time_slots = [
        #     (time(9, 0), time(10, 0)),   # 9:00 - 10:00
        #     (time(10, 0), time(11, 0)), # 10:00 - 11:00
        #     (time(11, 0), time(12, 0)), # 11:00 - 12:00
        # ]

        # for class_obj in classes:
        #     # Get subjects for this class
        #     subjects = db.query(Subject).filter(Subject.class_id == class_obj.id).order_by(Subject.order_in_class).all()

        #     if len(subjects) < 3:
        #         print(f"Warning: Class {class_obj.name} has only {len(subjects)} subjects, skipping timetable")
        #         continue

        #     for day in week_days:
        #         for i, time_slot in enumerate(time_slots):
        #             subject = subjects[i % len(subjects)]  # Cycle through subjects

        #             # Check if timetable entry already exists
        #             existing_timetable = db.query(Timetable).filter(
        #                 Timetable.class_id == class_obj.id,
        #                 Timetable.subject_id == subject.id,
        #                 Timetable.week_day == day,
        #                 Timetable.start_time == time_slot[0]
        #             ).first()

        #             if existing_timetable:
        #             print(f"Timetable entry already exists for {class_obj.name} {day} {time_slot[0]}")
        #             else:
        #                 new_timetable = Timetable(
        #                     class_id=class_obj.id,
        #                     subject_id=subject.id,
        #                     week_day=day,
        #                     start_time=time_slot[0],
        #                     end_time=time_slot[1],
        #                     is_active=True
        #                 )
        #                 db.add(new_timetable)
        #                 print(f"Created timetable: {class_obj.name} {day} {time_slot[0]}-{time_slot[1]} {subject.name}")

        # db.commit()
        print("Seed data creation completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error creating seed data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_school_data()