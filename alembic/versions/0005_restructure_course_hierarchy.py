"""
Restructure course hierarchy: Course -> Subject -> Lesson -> ClassSession

This migration restructures the database from:
  Course -> Class (year-based) -> Subject -> Session

To the new hierarchy:
  Course -> Subject (course-level) -> Lesson -> ClassSession (day-based)

Key changes:
1. Create new 'lessons' table
2. Create new 'class_sessions' table
3. Migrate subjects from class-level to course-level
4. Update foreign keys in chapters to reference lessons
5. Update attachments to reference lessons
6. Migrate session_contents to reference class_sessions

Revision ID: 0005_restructure_course_hierarchy
Revises: 0004_add_source_to_attachment
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '0005_restructure_course_hierarchy'
down_revision = '0004_add_source_to_attachment'
branch_labels = None
depends_on = None


def upgrade() -> None:
  # Step 1: Create lessons table
  op.create_table(
    'lessons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('order_in_subject', sa.Integer(), nullable=False, server_default='1'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
    sa.PrimaryKeyConstraint('id')
  )
  op.create_index(op.f('ix_lessons_subject_id'), 'lessons', ['subject_id'], unique=False)

  # Step 2: Create class_sessions table
  op.create_table(
    'class_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lesson_id', sa.Integer(), nullable=False),
    sa.Column('session_date', sa.Date(), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='0'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.PrimaryKeyConstraint('id')
  )
  op.create_index(op.f('ix_class_sessions_lesson_id'), 'class_sessions', ['lesson_id'], unique=False)

  # Step 3: Add course_id column to subjects (temporarily nullable)
  op.add_column('subjects', sa.Column('course_id', sa.Integer(), nullable=True))
  op.create_index(op.f('ix_subjects_course_id'), 'subjects', ['course_id'], unique=False)
  op.create_foreign_key(
    'fk_subjects_course_id',
    'subjects', 'courses',
    ['course_id'], ['id']
  )

  # Step 4: Migrate existing subjects data from class-level to course-level
  # Get the course_id from the class, then set it on the subject
  op.execute('''
    UPDATE subjects
    SET course_id = (
      SELECT course_id FROM classes WHERE classes.id = subjects.class_id
    )
    WHERE class_id IS NOT NULL
  ''')

  # Step 5: Make course_id NOT NULL now that data is migrated
  op.alter_column('subjects', 'course_id', nullable=False)

  # Step 6: Rename order_in_class to order_in_course
  with op.batch_alter_table('subjects', schema=None) as batch_op:
    batch_op.alter_column('order_in_class', new_column_name='order_in_course')

  # Step 7: Drop the old class_id foreign key constraint from subjects
  with op.batch_alter_table('subjects', schema=None) as batch_op:
    batch_op.drop_constraint('fk_subjects_class_id', type_='foreignkey')
    batch_op.drop_column('class_id')

  # Step 8: Update chapters to reference lessons instead of subjects
  # First add lesson_id column (temporarily nullable)
  op.add_column('chapters', sa.Column('lesson_id', sa.Integer(), nullable=True))
  op.create_index(op.f('ix_chapters_lesson_id'), 'chapters', ['lesson_id'], unique=False)
  op.create_foreign_key(
    'fk_chapters_lesson_id',
    'chapters', 'lessons',
    ['lesson_id'], ['id']
  )

  # For now, we'll create a default lesson for each subject to preserve existing data
  # In a real migration, you might handle this differently
  op.execute('''
    INSERT INTO lessons (subject_id, title, description, order_in_subject, created_at)
    SELECT id, 'Default Lesson', description, 1, datetime('now')
    FROM subjects
    WHERE id NOT IN (SELECT DISTINCT subject_id FROM lessons WHERE subject_id IS NOT NULL)
  ''')

  # Now populate chapter lesson_id - use the first lesson for each subject
  op.execute('''
    UPDATE chapters
    SET lesson_id = (
      SELECT id FROM lessons
      WHERE lessons.subject_id = (
        SELECT subject_id FROM sessions
        WHERE sessions.id = chapters.subject_id
      )
      LIMIT 1
    )
    WHERE subject_id IN (SELECT id FROM sessions)
  ''')

  # Make lesson_id NOT NULL after migration
  with op.batch_alter_table('chapters', schema=None) as batch_op:
    batch_op.alter_column('lesson_id', nullable=False)

  # Drop old subject_id from chapters
  with op.batch_alter_table('chapters', schema=None) as batch_op:
    batch_op.drop_constraint('fk_chapters_subject_id', type_='foreignkey')
    batch_op.drop_column('subject_id')

  # Step 9: Update attachments to support lesson_id
  op.add_column('attachments', sa.Column('lesson_id', sa.Integer(), nullable=True))
  op.create_index(op.f('ix_attachments_lesson_id'), 'attachments', ['lesson_id'], unique=False)
  op.create_foreign_key(
    'fk_attachments_lesson_id',
    'attachments', 'lessons',
    ['lesson_id'], ['id']
  )

  # Drop old subject_id from attachments if it exists
  with op.batch_alter_table('attachments', schema=None) as batch_op:
    batch_op.drop_constraint('fk_attachments_subject_id', type_='foreignkey')
    batch_op.drop_column('subject_id')

  # Step 10: Update session_contents to reference class_sessions instead of sessions
  # First add class_session_id column (temporarily nullable)
  op.add_column('session_contents', sa.Column('class_session_id', sa.Integer(), nullable=True))
  op.create_foreign_key(
    'fk_session_contents_class_session_id',
    'session_contents', 'class_sessions',
    ['class_session_id'], ['id']
  )

  # Create a class_session for each old session and migrate content
  op.execute('''
    INSERT INTO class_sessions (lesson_id, session_date, start_time, end_time, is_completed, created_at)
    SELECT 
      l.id,
      s.session_date,
      s.start_time,
      s.end_time,
      s.is_completed,
      s.created_at
    FROM sessions s
    JOIN subjects subj ON s.subject_id = subj.id
    JOIN lessons l ON l.subject_id = subj.id
    WHERE l.order_in_subject = 1  -- Use first lesson for each subject
  ''')

  # Migrate session_contents to class_sessions
  op.execute('''
    UPDATE session_contents
    SET class_session_id = (
      SELECT cs.id FROM class_sessions cs
      JOIN sessions s ON (
        s.session_date = cs.session_date AND
        s.start_time = cs.start_time AND
        s.end_time = cs.end_time
      )
      WHERE s.id = session_contents.session_id
      LIMIT 1
    )
    WHERE session_id IS NOT NULL
  ''')

  # Make class_session_id NOT NULL
  op.alter_column('session_contents', 'class_session_id', nullable=False)

  # Drop old session_id from session_contents
  with op.batch_alter_table('session_contents', schema=None) as batch_op:
    batch_op.drop_constraint('fk_session_contents_session_id', type_='foreignkey')
    batch_op.drop_column('session_id')

  print("✅ Database migration completed: Course hierarchy restructured")


def downgrade() -> None:
  # Reverse the migration steps
  
  # Step 1: Restore session_id to session_contents
  op.add_column('session_contents', sa.Column('session_id', sa.Integer(), nullable=True))
  op.create_foreign_key(
    'fk_session_contents_session_id',
    'session_contents', 'sessions',
    ['session_id'], ['id']
  )
  
  with op.batch_alter_table('session_contents', schema=None) as batch_op:
    batch_op.drop_constraint('fk_session_contents_class_session_id', type_='foreignkey')
    batch_op.drop_column('class_session_id')

  # Step 2: Restore subject_id to attachments
  op.add_column('attachments', sa.Column('subject_id', sa.Integer(), nullable=True))
  op.create_foreign_key(
    'fk_attachments_subject_id',
    'attachments', 'subjects',
    ['subject_id'], ['id']
  )
  
  with op.batch_alter_table('attachments', schema=None) as batch_op:
    batch_op.drop_constraint('fk_attachments_lesson_id', type_='foreignkey')
    batch_op.drop_index('ix_attachments_lesson_id')
    batch_op.drop_column('lesson_id')

  # Step 3: Restore subject_id to chapters
  op.add_column('chapters', sa.Column('subject_id', sa.Integer(), nullable=True))
  op.create_foreign_key(
    'fk_chapters_subject_id',
    'chapters', 'subjects',
    ['subject_id'], ['id']
  )
  
  with op.batch_alter_table('chapters', schema=None) as batch_op:
    batch_op.drop_constraint('fk_chapters_lesson_id', type_='foreignkey')
    batch_op.drop_index('ix_chapters_lesson_id')
    batch_op.drop_column('lesson_id')

  # Step 4: Restore class_id to subjects
  op.add_column('subjects', sa.Column('class_id', sa.Integer(), nullable=True))
  op.create_foreign_key(
    'fk_subjects_class_id',
    'subjects', 'classes',
    ['class_id'], ['id']
  )
  
  # Restore order_in_class
  with op.batch_alter_table('subjects', schema=None) as batch_op:
    batch_op.alter_column('order_in_course', new_column_name='order_in_class')
    batch_op.drop_constraint('fk_subjects_course_id', type_='foreignkey')
    batch_op.drop_index('ix_subjects_course_id')
    batch_op.drop_column('course_id')

  # Step 5: Drop class_sessions and lessons tables
  op.drop_index('ix_class_sessions_lesson_id', table_name='class_sessions')
  op.drop_table('class_sessions')
  
  op.drop_index('ix_lessons_subject_id', table_name='lessons')
  op.drop_table('lessons')

  print("✅ Database migration reversed")
