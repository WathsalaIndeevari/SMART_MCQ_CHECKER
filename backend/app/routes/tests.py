from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_file

from app.authz import get_owned_test, teacher_required
from app.csv_key import CsvValidationError, parse_answer_key_csv
from app.extensions import db
from app.models import Question, Test
from app.uploads import allowed_csv, allowed_image, generate_test_code, save_upload
from ml_pipeline.extract_layout import LayoutError, extract_layout

tests_bp = Blueprint("tests", __name__)


def _maybe_activate(test):
    if test.layout_json and test.questions:
        test.status = "ACTIVE"


def _apply_answer_key(test, positions):
    test.questions.clear()
    db.session.flush()
    for index, position in enumerate(positions, start=1):
        test.questions.append(
            Question(question_number=index, correct_position=position)
        )


def _process_template(test, file_storage):
    if not file_storage or not file_storage.filename:
        raise ValueError("A blank OMR template image is required.")
    if not allowed_image(file_storage.filename):
        raise ValueError("Template must be a JPG, JPEG, or PNG file.")

    dest = Path(current_app.config["UPLOAD_FOLDER"]) / "templates"
    path = save_upload(file_storage, dest, prefix=f"template_{test.id}")
    result = extract_layout(path, test.question_count, test.choice_count)
    test.template_path = path
    test.template_width = result["width"]
    test.template_height = result["height"]
    test.layout_json = result["layout"]
    return result


def _process_csv(test, file_storage):
    if not file_storage or not file_storage.filename:
        raise ValueError("An answer-key CSV is required.")
    if not allowed_csv(file_storage.filename):
        raise ValueError("Answer key must be a CSV file.")
    positions = parse_answer_key_csv(
        file_storage,
        test.question_count,
        test.choice_count,
        expected_test_code=test.test_code,
    )
    _apply_answer_key(test, positions)
    return positions


@tests_bp.post("/")
@teacher_required
def create_test(user):
    title = (request.form.get("title") or "").strip()
    try:
        question_count = int(request.form.get("question_count", 0))
        choice_count = int(request.form.get("choice_count", 0))
    except ValueError:
        return jsonify({"error": "question_count and choice_count must be integers."}), 400

    answer_style = (request.form.get("answer_style") or "ALPHABETIC").strip().upper()
    if not title:
        return jsonify({"error": "Test title is required."}), 400
    if question_count < 1:
        return jsonify({"error": "Number of questions must be at least 1."}), 400
    if choice_count < 2 or choice_count > 5:
        return jsonify({"error": "Number of choices must be between 2 and 5."}), 400
    if answer_style not in {"ALPHABETIC", "NUMERIC"}:
        return jsonify({"error": "answer_style must be ALPHABETIC or NUMERIC."}), 400

    test = Test(
        test_code=generate_test_code(),
        teacher_id=user.id,
        title=title,
        question_count=question_count,
        choice_count=choice_count,
        answer_style=answer_style,
        status="DRAFT",
    )
    db.session.add(test)
    db.session.flush()

    template_info = None
    try:
        if "blank_template" in request.files:
            template_info = _process_template(test, request.files["blank_template"])
        if "answer_key_csv" in request.files:
            _process_csv(test, request.files["answer_key_csv"])
        _maybe_activate(test)
        db.session.commit()
    except (LayoutError, CsvValidationError, ValueError) as exc:
        db.session.commit()
        return jsonify(
            {
                "error": f"{exc} Draft saved as {test.test_code}." if test.id else str(exc),
                "test": test.to_dict(),
            }
        ), 400

    payload = test.to_dict()
    if template_info:
        payload["template_status"] = {
            "valid": True,
            "questions_detected": template_info["questions_detected"],
            "choices_per_question": template_info["choices_per_question"],
            "message": "Template processed successfully",
        }
    return jsonify(payload), 201


@tests_bp.get("/")
@teacher_required
def list_tests(user):
    tests = Test.query.filter_by(teacher_id=user.id).order_by(Test.created_at.desc()).all()
    return jsonify([item.to_dict() for item in tests])


@tests_bp.get("/<test_id>")
@teacher_required
def get_test(user, test_id):
    test, error = get_owned_test(user, test_id)
    if error:
        return error
    return jsonify(test.to_dict(include_layout=True))


@tests_bp.put("/<test_id>")
@teacher_required
def update_test(user, test_id):
    test, error = get_owned_test(user, test_id)
    if error:
        return error
    data = request.get_json(silent=True) or {}
    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "Title cannot be empty."}), 400
        test.title = title
    if "status" in data:
        status = str(data["status"]).upper()
        if status not in {"DRAFT", "ACTIVE", "CLOSED"}:
            return jsonify({"error": "Invalid status."}), 400
        if status == "ACTIVE" and (not test.layout_json or not test.questions):
            return jsonify({"error": "A test cannot be used until its template and answer key are validated."}), 400
        test.status = status
    db.session.commit()
    return jsonify(test.to_dict())


@tests_bp.delete("/<test_id>")
@teacher_required
def delete_test(user, test_id):
    test, error = get_owned_test(user, test_id)
    if error:
        return error
    db.session.delete(test)
    db.session.commit()
    return jsonify({"ok": True})


@tests_bp.post("/<test_id>/template")
@teacher_required
def upload_template(user, test_id):
    test, error = get_owned_test(user, test_id)
    if error:
        return error
    try:
        result = _process_template(test, request.files.get("blank_template"))
        _maybe_activate(test)
        db.session.commit()
    except (LayoutError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"valid": False, "message": str(exc)}), 400
    return jsonify(
        {
            "valid": True,
            "questions_detected": result["questions_detected"],
            "choices_per_question": result["choices_per_question"],
            "message": "Template processed successfully",
        }
    )


@tests_bp.get("/<test_id>/template-file")
@teacher_required
def template_file(user, test_id):
    test, error = get_owned_test(user, test_id)
    if error:
        return error
    if not test.template_path:
        return jsonify({"error": "No template uploaded."}), 404
    return send_file(test.template_path)


@tests_bp.get("/<test_id>/template-status")
@teacher_required
def template_status(user, test_id):
    test, error = get_owned_test(user, test_id)
    if error:
        return error
    valid = bool(test.layout_json)
    return jsonify(
        {
            "valid": valid,
            "questions_detected": len(test.layout_json or {}),
            "choices_per_question": test.choice_count,
            "template_width": test.template_width,
            "template_height": test.template_height,
            "message": "Template processed successfully" if valid else "No valid template yet",
        }
    )


@tests_bp.post("/<test_id>/answer-key")
@teacher_required
def upload_answer_key(user, test_id):
    test, error = get_owned_test(user, test_id)
    if error:
        return error
    try:
        _process_csv(test, request.files.get("answer_key_csv"))
        _maybe_activate(test)
        db.session.commit()
    except (CsvValidationError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    return jsonify(test.to_dict())
