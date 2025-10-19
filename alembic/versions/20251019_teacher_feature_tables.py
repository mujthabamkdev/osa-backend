"""Add tables for teacher assessments and lesson Q&A

Revision ID: 20251019_teacher_feature_tables
Revises: cde02ae167c9
Create Date: 2025-10-19 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251019_teacher_feature_tables"
down_revision: Union[str, None] = "cde02ae167c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.create_table(
    "exams",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
    sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id"), nullable=True),
    sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("title", sa.String(length=255), nullable=False),
    sa.Column("description", sa.Text(), nullable=False, server_default=""),
    sa.Column("scheduled_date", sa.DateTime(timezone=True), nullable=True),
    sa.Column("duration_minutes", sa.Integer(), nullable=True),
    sa.Column("max_score", sa.Integer(), nullable=True),
    sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
  )
  op.create_index("ix_exams_course_id", "exams", ["course_id"])
  op.create_index("ix_exams_subject_id", "exams", ["subject_id"])
  op.create_index("ix_exams_teacher_id", "exams", ["teacher_id"])

  op.create_table(
    "exam_results",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("exam_id", sa.Integer(), sa.ForeignKey("exams.id"), nullable=False),
    sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("score", sa.Integer(), nullable=False),
    sa.Column("max_score", sa.Integer(), nullable=True),
    sa.Column("status", sa.String(length=50), nullable=True),
    sa.Column("feedback", sa.Text(), nullable=True),
    sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
  )
  op.create_index("ix_exam_results_exam_id", "exam_results", ["exam_id"])
  op.create_index("ix_exam_results_student_id", "exam_results", ["student_id"])

  op.create_table(
    "lesson_questions",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lessons.id"), nullable=False),
    sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    sa.Column("question", sa.Text(), nullable=False),
    sa.Column("is_anonymous", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
  )
  op.create_index("ix_lesson_questions_lesson_id", "lesson_questions", ["lesson_id"])
  op.create_index("ix_lesson_questions_student_id", "lesson_questions", ["student_id"])

  op.create_table(
    "lesson_answers",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("question_id", sa.Integer(), sa.ForeignKey("lesson_questions.id"), nullable=False),
    sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("answer", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
  )
  op.create_index("ix_lesson_answers_question_id", "lesson_answers", ["question_id"])
  op.create_index("ix_lesson_answers_teacher_id", "lesson_answers", ["teacher_id"])


def downgrade() -> None:
  op.drop_index("ix_lesson_answers_teacher_id", table_name="lesson_answers")
  op.drop_index("ix_lesson_answers_question_id", table_name="lesson_answers")
  op.drop_table("lesson_answers")

  op.drop_index("ix_lesson_questions_student_id", table_name="lesson_questions")
  op.drop_index("ix_lesson_questions_lesson_id", table_name="lesson_questions")
  op.drop_table("lesson_questions")

  op.drop_index("ix_exam_results_student_id", table_name="exam_results")
  op.drop_index("ix_exam_results_exam_id", table_name="exam_results")
  op.drop_table("exam_results")

  op.drop_index("ix_exams_teacher_id", table_name="exams")
  op.drop_index("ix_exams_subject_id", table_name="exams")
  op.drop_index("ix_exams_course_id", table_name="exams")
  op.drop_table("exams")
