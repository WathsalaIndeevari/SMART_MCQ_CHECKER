from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON as GenericJSON
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

JSONType = GenericJSON().with_variant(JSON, "postgresql")


def utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="TEACHER", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    tests: Mapped[list["Test"]] = relationship(back_populates="teacher")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Test(db.Model):
    __test__ = False
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    question_count: Mapped[int] = mapped_column(Integer, nullable=False)
    choice_count: Mapped[int] = mapped_column(Integer, nullable=False)
    answer_style: Mapped[str] = mapped_column(String(20), default="ALPHABETIC", nullable=False)
    template_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    template_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    template_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    layout_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    teacher: Mapped[User] = relationship(back_populates="tests")
    questions: Mapped[list["Question"]] = relationship(
        back_populates="test", cascade="all, delete-orphan", order_by="Question.question_number"
    )
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="test", cascade="all, delete-orphan"
    )

    def to_dict(self, include_layout=False):
        data = {
            "id": self.id,
            "test_code": self.test_code,
            "teacher_id": self.teacher_id,
            "title": self.title,
            "question_count": self.question_count,
            "choice_count": self.choice_count,
            "answer_style": self.answer_style,
            "template_path": self.template_path,
            "template_width": self.template_width,
            "template_height": self.template_height,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "submission_count": len(self.submissions) if self.submissions is not None else 0,
            "answer_key": [
                {
                    "question_number": q.question_number,
                    "correct_position": q.correct_position,
                }
                for q in (self.questions or [])
            ],
        }
        if include_layout:
            data["layout_json"] = self.layout_json
        return data


class Question(db.Model):
    __tablename__ = "questions"
    __table_args__ = (UniqueConstraint("test_id", "question_number", name="uq_test_question"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_position: Mapped[int] = mapped_column(Integer, nullable=False)

    test: Mapped[Test] = relationship(back_populates="questions")


class Submission(db.Model):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    student_id: Mapped[str] = mapped_column(String(80), nullable=False)
    student_name: Mapped[str] = mapped_column(String(120), nullable=False)
    sheet_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    incorrect_count: Mapped[int] = mapped_column(Integer, default=0)
    unanswered_count: Mapped[int] = mapped_column(Integer, default=0)
    multiple_count: Mapped[int] = mapped_column(Integer, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    percentage: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="COMPLETED", nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    test: Mapped[Test] = relationship(back_populates="submissions")
    answers: Mapped[list["SubmissionAnswer"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )

    def to_summary(self):
        return {
            "submission_id": self.id,
            "student_id": self.student_id,
            "student_name": self.student_name,
            "test_id": self.test.test_code if self.test else None,
            "score": self.correct_count,
            "total": self.total_questions,
            "percentage": round(self.percentage, 2),
            "correct_count": self.correct_count,
            "incorrect_count": self.incorrect_count,
            "unanswered_count": self.unanswered_count,
            "multiple_count": self.multiple_count,
            "status": self.status,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }


class SubmissionAnswer(db.Model):
    __tablename__ = "submission_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    detected_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    correct_position: Mapped[int] = mapped_column(Integer, nullable=False)
    fill_scores: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)

    submission: Mapped[Submission] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship()
