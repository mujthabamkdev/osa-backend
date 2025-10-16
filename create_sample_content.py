#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.chapter import Chapter, Attachment, Quiz, QuizQuestion, LessonProgress
import json

def create_sample_course_content():
    db = SessionLocal()

    try:
        # Use existing course with ID 1
        from app.models.course import Course
        course = db.query(Course).filter(Course.id == 1).first()
        if not course:
            print("Course with ID 1 not found. Please create a course first.")
            return

        # Create chapters
        chapter1 = Chapter(
            course_id=1,
            title="Introduction to Islamic Studies",
            description="Learn the basics of Islamic teachings and principles",
            order=1
        )
        db.add(chapter1)

        chapter2 = Chapter(
            course_id=1,
            title="The Five Pillars of Islam",
            description="Understanding the fundamental practices of Islam",
            order=2
        )
        db.add(chapter2)

        db.commit()

        # Create attachments for chapter 1
        attachment1 = Attachment(
            chapter_id=chapter1.id,
            title="Welcome to Islamic Studies",
            file_type="video",
            file_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Sample YouTube video
            description="Introduction video to Islamic Studies"
        )
        db.add(attachment1)

        attachment2 = Attachment(
            chapter_id=chapter1.id,
            title="Islamic Studies Guide",
            file_type="document",
            file_url="https://example.com/guide.pdf",
            description="Comprehensive guide to Islamic Studies"
        )
        db.add(attachment2)

        # Create quiz for chapter 1
        quiz1 = Quiz(
            chapter_id=chapter1.id,
            title="Islamic Studies Basics Quiz",
            description="Test your knowledge of Islamic Studies fundamentals",
            passing_score=70
        )
        db.add(quiz1)

        db.commit()

        # Create quiz questions
        question1 = QuizQuestion(
            quiz_id=quiz1.id,
            question="What is the meaning of 'Islam'?",
            options=json.dumps(["Submission to God", "Peace", "Faith", "Both A and B"]),
            correct_answer=3,  # Index of correct answer (0-based)
            order=1
        )
        db.add(question1)

        question2 = QuizQuestion(
            quiz_id=quiz1.id,
            question="How many pillars are there in Islam?",
            options=json.dumps(["3", "5", "7", "10"]),
            correct_answer=1,
            order=2
        )
        db.add(question2)

        question3 = QuizQuestion(
            quiz_id=quiz1.id,
            question="What is the holy book of Islam called?",
            options=json.dumps(["Bible", "Torah", "Quran", "Vedas"]),
            correct_answer=2,
            order=3
        )
        db.add(question3)

        # Create attachments for chapter 2
        attachment3 = Attachment(
            chapter_id=chapter2.id,
            title="The Five Pillars Explained",
            file_type="video",
            file_url="https://www.youtube.com/watch?v=example2",
            description="Detailed explanation of the Five Pillars"
        )
        db.add(attachment3)

        # Create quiz for chapter 2
        quiz2 = Quiz(
            chapter_id=chapter2.id,
            title="Five Pillars Quiz",
            description="Test your understanding of the Five Pillars of Islam",
            passing_score=75
        )
        db.add(quiz2)

        db.commit()

        # Create quiz questions for chapter 2
        question4 = QuizQuestion(
            quiz_id=quiz2.id,
            question="Which of the following is NOT one of the Five Pillars?",
            options=json.dumps(["Salah", "Zakat", "Hajj", "Ramadan fasting"]),
            correct_answer=3,
            order=1
        )
        db.add(question4)

        question5 = QuizQuestion(
            quiz_id=quiz2.id,
            question="How many times a day do Muslims pray Salah?",
            options=json.dumps(["3", "5", "7", "10"]),
            correct_answer=1,
            order=2
        )
        db.add(question5)

        db.commit()

        print("Sample course content created successfully!")
        print(f"Created {db.query(Chapter).count()} chapters")
        print(f"Created {db.query(Attachment).count()} attachments")
        print(f"Created {db.query(Quiz).count()} quizzes")
        print(f"Created {db.query(QuizQuestion).count()} quiz questions")

    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_course_content()