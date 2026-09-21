import csv
import io
from pathlib import Path

from flask import Blueprint, Response, current_app, jsonify, request

from app.authz import find_test, get_owned_test, teacher_required
from app.extensions import db
from app.models import Submission, SubmissionAnswer, Test
from app.scoring import summarize_results
from app.serializers import serialize_evaluation
from app.uploads import allowed_image, save_upload
from ml_pipeline.evaluate_sheet import EvaluationError, evaluate_sheet

submissions_bp = Blueprint("submissions", __name__)


@submissions_bp.get("/dashboard")
@teacher_required
def dashboard(user):
    tests = Test.query.filter_by(teacher_id=user.id).all()
    submissions = (
        Submission.query.join(Test)
        .filter(Test.teacher_id == user.id)
        .order_by(Submission.submitted_at.desc())
        .limit(8)
        .all()
    )
    return jsonify(
        {
            "total_tests": len(tests),
            "active_tests": sum(1 for item in tests if item.status == "ACTIVE"),
            "total_submissions": Submission.query.join(Test)
            .filter(Test.teacher_id == user.id)
            .count(),
            "recent_results": [item.to_summary() for item in submissions],
        }
    )


@submissions_bp.post("/tests/<test_id>/submissions")
def create_submission(test_id):
    test = find_test(test_id)
    if test is None:
        return jsonify({"error": "Test not found. Check the Test ID."}), 404
    if test.status != "ACTIVE":
        return jsonify({"error": "This test is not accepting submissions yet."}), 400
    if not test.layout_json or not test.questions:
        return jsonify({"error": "This test is missing a validated template or answer key."}), 400

    student_id = (request.form.get("student_id") or "").strip()
    student_name = (request.form.get("student_name") or "").strip()
    sheet = request.files.get("sheet") or request.files.get("answer_sheet")
    if not student_id or not student_name:
        return jsonify({"error": "Student ID and name are required."}), 400
    if not sheet or not sheet.filename:
        return jsonify({"error": "Please upload a completed answer sheet."}), 400
    if not allowed_image(sheet.filename):
        return jsonify({"error": "Answer sheet must be a JPG, JPEG, or PNG file."}), 400

    dest = Path(current_app.config["UPLOAD_FOLDER"]) / "sheets"
    path = save_upload(sheet, dest, prefix=f"sheet_{test.id}_{student_id}")

    try:
        question_results = evaluate_sheet(
            path,
            test.layout_json,
            test.questions,
            test.template_width,
            test.template_height,
            mark_threshold=current_app.config.get("MARK_THRESHOLD", 0.35),
            review_margin=current_app.config.get("REVIEW_MARGIN", 0.08),
        )
    except EvaluationError as exc:
        return jsonify({"error": str(exc)}), 400

    summary = summarize_results(question_results, test.question_count)
    questions_by_number = {q.question_number: q for q in test.questions}

    submission = Submission(
        test_id=test.id,
        student_id=student_id,
        student_name=student_name,
        sheet_path=path,
        correct_count=summary["correct_count"],
        incorrect_count=summary["incorrect_count"],
        unanswered_count=summary["unanswered_count"],
        multiple_count=summary["multiple_count"],
        total_questions=summary["total_questions"],
        percentage=summary["percentage"],
        status=summary["status"],
    )
    db.session.add(submission)
    db.session.flush()

    for item in question_results:
        question = questions_by_number[item["question_number"]]
        db.session.add(
            SubmissionAnswer(
                submission_id=submission.id,
                question_id=question.id,
                detected_position=item["detected_position"],
                correct_position=item["correct_position"],
                fill_scores=item["fill_scores"],
                confidence=item["confidence"],
                status=item["status"],
            )
        )
    db.session.commit()
    return jsonify(serialize_evaluation(submission, test)), 201


@submissions_bp.get("/tests/<test_id>/submissions")
@teacher_required
def list_submissions(user, test_id):
    test, error = get_owned_test(user, test_id)
    if error:
        return error
    items = (
        Submission.query.filter_by(test_id=test.id)
        .order_by(Submission.submitted_at.desc())
        .all()
    )
    return jsonify([item.to_summary() for item in items])


@submissions_bp.get("/tests/<test_id>/results")
@teacher_required
def test_results(user, test_id):
    return list_submissions(user, test_id)


@submissions_bp.get("/submissions/<int:submission_id>")
def get_submission(submission_id):
    submission = db.session.get(Submission, submission_id)
    if not submission:
        return jsonify({"error": "Submission not found."}), 404
    return jsonify(serialize_evaluation(submission, submission.test))


@submissions_bp.get("/submissions/<int:submission_id>/results")
def get_submission_results(submission_id):
    return get_submission(submission_id)


@submissions_bp.get("/submissions/<int:submission_id>/download")
def download_submission(submission_id):
    submission = db.session.get(Submission, submission_id)
    if not submission:
        return jsonify({"error": "Submission not found."}), 404
    payload = serialize_evaluation(submission, submission.test)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "student_id",
            "student_name",
            "test_id",
            "score",
            "total",
            "percentage",
            "status",
        ]
    )
    writer.writerow(
        [
            payload["student_id"],
            payload["student_name"],
            payload["test_id"],
            payload["score"],
            payload["total"],
            payload["percentage"],
            payload["status"],
        ]
    )
    writer.writerow([])
    writer.writerow(
        ["question_number", "detected_label", "correct_label", "status", "confidence"]
    )
    for question in payload["questions"]:
        writer.writerow(
            [
                question["question_number"],
                question["detected_label"],
                question["correct_label"],
                question["status"],
                question["confidence"],
            ]
        )
    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=submission_{submission.id}.csv"
        },
    )
