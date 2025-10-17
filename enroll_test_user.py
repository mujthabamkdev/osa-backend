#!/usr/bin/env python3
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

def enroll_test_user():
    db = SessionLocal()

    try:
        # First, add the missing active_class_id column if it doesn't exist
        try:
            db.execute(text("ALTER TABLE enrollments ADD COLUMN active_class_id INTEGER REFERENCES chapters(id)"))
            print("Added active_class_id column to enrollments table")
        except Exception as e:
            print(f"Column might already exist: {e}")

        # Get test user
        result = db.execute(text("SELECT id FROM users WHERE email = 'test@test.com'"))
        user_row = result.fetchone()
        if not user_row:
            print("Test user not found")
            return

        user_id = user_row[0]
        print(f"Found test user with ID: {user_id}")

        # Check if already enrolled
        result = db.execute(text("SELECT id FROM enrollments WHERE student_id = :student_id AND course_id = :course_id"), {"student_id": user_id, "course_id": 1})
        existing = result.fetchone()

        if existing:
            print("Test user is already enrolled in course 1")
        else:
            # Enroll the user
            db.execute(text("""
                INSERT INTO enrollments (student_id, course_id, active_class_id, enrolled_at, is_active)
                VALUES (:student_id, :course_id, :active_class_id, :enrolled_at, :is_active)
            """), {
                "student_id": user_id,
                "course_id": 1,
                "active_class_id": 7,  # Class One - Swarf
                "enrolled_at": datetime.utcnow(),
                "is_active": True
            })

            print("Successfully enrolled test user in course 1")
            print("Set active class to 'Class One - Swarf' (ID: 7)")

        # Set active class for the enrollment (first subject)
        db.execute(text("""
            UPDATE enrollments
            SET active_class_id = :active_class_id
            WHERE student_id = :student_id AND course_id = :course_id
        """), {
            "active_class_id": 7,  # Class One - Swarf
            "student_id": user_id,
            "course_id": 1
        })

        db.commit()

        # Verify enrollment
        result = db.execute(text("""
            SELECT e.id, e.student_id, e.course_id, e.active_class_id, c.title as active_class_title
            FROM enrollments e
            LEFT JOIN chapters c ON e.active_class_id = c.id
            WHERE e.student_id = :student_id
        """), {"student_id": user_id})

        enrollment = result.fetchone()
        if enrollment:
            print("\nEnrollment verified:")
            print(f"Enrollment ID: {enrollment[0]}")
            print(f"Student ID: {enrollment[1]}")
            print(f"Course ID: {enrollment[2]}")
            print(f"Active Class ID: {enrollment[3]}")
            print(f"Active Class Title: {enrollment[4]}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    enroll_test_user()