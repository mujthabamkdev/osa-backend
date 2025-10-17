#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.course import Course
from app.models.chapter import Chapter, Attachment, Quiz, QuizQuestion, LessonProgress

def update_course_and_create_levels():
    db = SessionLocal()

    try:
        # Update course title
        course = db.query(Course).filter(Course.id == 1).first()
        if course:
            course.title = "Online Sharia"
            print(f"✓ Updated course title to: {course.title}")
        else:
            print("Course with ID 1 not found")
            return

        # Delete related data first to avoid foreign key issues
        # Delete lesson progress
        progress_deleted = db.query(LessonProgress).filter(
            LessonProgress.chapter_id.in_(
                db.query(Chapter.id).filter(Chapter.course_id == 1)
            )
        ).delete(synchronize_session=False)
        print(f"✓ Deleted {progress_deleted} lesson progress records")

        # Delete quiz questions
        questions_deleted = db.query(QuizQuestion).filter(
            QuizQuestion.quiz_id.in_(
                db.query(Quiz.id).filter(
                    Quiz.chapter_id.in_(
                        db.query(Chapter.id).filter(Chapter.course_id == 1)
                    )
                )
            )
        ).delete(synchronize_session=False)
        print(f"✓ Deleted {questions_deleted} quiz questions")

        # Delete quizzes
        quizzes_deleted = db.query(Quiz).filter(
            Quiz.chapter_id.in_(
                db.query(Chapter.id).filter(Chapter.course_id == 1)
            )
        ).delete(synchronize_session=False)
        print(f"✓ Deleted {quizzes_deleted} quizzes")

        # Delete attachments
        attachments_deleted = db.query(Attachment).filter(Attachment.chapter_id.in_(
            db.query(Chapter.id).filter(Chapter.course_id == 1)
        )).delete(synchronize_session=False)
        print(f"✓ Deleted {attachments_deleted} attachments")

        # Delete existing chapters
        chapters_deleted = db.query(Chapter).filter(Chapter.course_id == 1).delete()
        print(f"✓ Deleted {chapters_deleted} existing chapters")

        # Create 5 new levels (Class 1-5)
        levels = [
            ("Class 1", "Foundation level of Online Sharia studies"),
            ("Class 2", "Intermediate level covering basic principles"),
            ("Class 3", "Advanced foundational concepts"),
            ("Class 4", "Comprehensive understanding and application"),
            ("Class 5", "Mastery level with advanced topics")
        ]

        for i, (title, description) in enumerate(levels, 1):
            chapter = Chapter(
                course_id=1,
                title=title,
                description=description,
                order=i
            )
            db.add(chapter)

        db.commit()
        print("✓ Created 5 new levels (Class 1-5)")

        # Verify the changes
        updated_course = db.query(Course).filter(Course.id == 1).first()
        chapters = db.query(Chapter).filter(Chapter.course_id == 1).order_by(Chapter.order).all()

        print("\n📚 Course Structure:")
        print(f"Course: {updated_course.title}")
        print("Levels:")
        for chapter in chapters:
            print(f"  {chapter.order}. {chapter.title} - {chapter.description}")

    except Exception as e:
        print(f"❌ Error updating course: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_course_and_create_levels()