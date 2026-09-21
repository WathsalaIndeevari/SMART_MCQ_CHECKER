"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-09-21
"""

from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "tests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("test_code", sa.String(length=40), nullable=False, unique=True),
        sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("choice_count", sa.Integer(), nullable=False),
        sa.Column("answer_style", sa.String(length=20), nullable=False),
        sa.Column("template_path", sa.String(length=500), nullable=True),
        sa.Column("template_width", sa.Integer(), nullable=True),
        sa.Column("template_height", sa.Integer(), nullable=True),
        sa.Column("layout_json", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("test_id", sa.Integer(), sa.ForeignKey("tests.id"), nullable=False),
        sa.Column("question_number", sa.Integer(), nullable=False),
        sa.Column("correct_position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("test_id", "question_number", name="uq_test_question"),
    )
    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("test_id", sa.Integer(), sa.ForeignKey("tests.id"), nullable=False),
        sa.Column("student_id", sa.String(length=80), nullable=False),
        sa.Column("student_name", sa.String(length=120), nullable=False),
        sa.Column("sheet_path", sa.String(length=500), nullable=True),
        sa.Column("correct_count", sa.Integer(), nullable=True),
        sa.Column("incorrect_count", sa.Integer(), nullable=True),
        sa.Column("unanswered_count", sa.Integer(), nullable=True),
        sa.Column("multiple_count", sa.Integer(), nullable=True),
        sa.Column("total_questions", sa.Integer(), nullable=True),
        sa.Column("percentage", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "submission_answers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("submission_id", sa.Integer(), sa.ForeignKey("submissions.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("detected_position", sa.Integer(), nullable=True),
        sa.Column("correct_position", sa.Integer(), nullable=False),
        sa.Column("fill_scores", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
    )


def downgrade():
    op.drop_table("submission_answers")
    op.drop_table("submissions")
    op.drop_table("questions")
    op.drop_table("tests")
    op.drop_table("users")
