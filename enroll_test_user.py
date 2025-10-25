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
                INSERT INTO enrollments (student_id, course_id, class_id, enrolled_at, is_active)
                VALUES (:student_id, :course_id, :class_id, :enrolled_at, :is_active)
            """), {
                "student_id": user_id,
                "course_id": 1,
                "class_id": 1,
                "enrolled_at": datetime.utcnow(),
                "is_active": True
            })

            print("Successfully enrolled test user in course 1")
            print("Set class to ID 1")

        # Update class for the enrollment if needed
        db.execute(text("""
            UPDATE enrollments
            SET class_id = :class_id
            WHERE student_id = :student_id AND course_id = :course_id
        """), {
            "class_id": 1,
            "student_id": user_id,
            "course_id": 1
        })

        db.commit()

        # Verify enrollment
        result = db.execute(text("""
            SELECT e.id, e.student_id, e.course_id, e.class_id, c.name as class_name
            FROM enrollments e
            LEFT JOIN classes c ON e.class_id = c.id
            WHERE e.student_id = :student_id
        """), {"student_id": user_id})

        enrollment = result.fetchone()
        if enrollment:
            print("\nEnrollment verified:")
            print(f"Enrollment ID: {enrollment[0]}")
            print(f"Student ID: {enrollment[1]}")
            print(f"Course ID: {enrollment[2]}")
            print(f"Class ID: {enrollment[3]}")
            print(f"Class Name: {enrollment[4]}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    enroll_test_user()