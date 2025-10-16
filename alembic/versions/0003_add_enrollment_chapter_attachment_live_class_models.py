from alembic import op
import sqlalchemy as sa

revision = "0003_add_enrollment_chapter_attachment_live_class_models"
down_revision = "0002_add_notes_table"
branch_labels = None
depends_on = None

def upgrade():
    # Create enrollments table
    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean(), default=True),
    )

    # Create chapters table
    op.create_table(
        "chapters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create attachments table
    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=True),
        sa.Column("chapter_id", sa.Integer(), sa.ForeignKey("chapters.id"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("file_type", sa.Enum('VIDEO', 'DOCUMENT', 'IMAGE', 'AUDIO', name='attachmenttype'), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create live_classes table
    op.create_table(
        "live_classes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("chapter_id", sa.Integer(), sa.ForeignKey("chapters.id"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("scheduled_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("meeting_link", sa.String(500), nullable=True),
        sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create quizzes table
    op.create_table(
        "quizzes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("chapter_id", sa.Integer(), sa.ForeignKey("chapters.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("passing_score", sa.Integer(), nullable=False, default=70),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create quiz_questions table
    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("quiz_id", sa.Integer(), sa.ForeignKey("quizzes.id"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("options", sa.Text(), nullable=False),
        sa.Column("correct_answer", sa.Integer(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, default=1),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create lesson_progress table
    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("chapter_id", sa.Integer(), sa.ForeignKey("chapters.id"), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, default=False),
        sa.Column("quiz_score", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Add chapter_id to notes table (without foreign key for SQLite compatibility)
    op.add_column("notes", sa.Column("chapter_id", sa.Integer(), nullable=True))

def downgrade():
    # Remove chapter_id from notes table
    op.drop_column("notes", "chapter_id")

    # Drop tables in reverse order
    op.drop_table("lesson_progress")
    op.drop_table("quiz_questions")
    op.drop_table("quizzes")
    op.drop_table("live_classes")
    op.drop_table("attachments")
    op.drop_table("chapters")
    op.drop_table("enrollments")