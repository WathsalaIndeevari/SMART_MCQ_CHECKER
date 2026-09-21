from io import BytesIO
from unittest.mock import patch

from app.extensions import db
from app.models import Question, Test


def test_register_and_me(client):
    created = client.post(
        "/api/auth/register",
        json={"name": "Pat", "email": "pat@school.edu", "password": "secret123"},
    )
    assert created.status_code == 201
    token = created.get_json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.get_json()["email"] == "pat@school.edu"


def test_login_rejects_bad_password(client, auth_headers):
    response = client.post(
        "/api/auth/login",
        json={"email": "ada@school.edu", "password": "nope"},
    )
    assert response.status_code == 401


def test_create_test_requires_auth(client):
    response = client.post("/api/tests/", data={"title": "Quiz"})
    assert response.status_code == 401


@patch("app.routes.tests.extract_layout")
def test_create_test_with_mocked_cv(extract_layout, client, auth_headers, app):
    extract_layout.return_value = {
        "layout": {"1": [[1, 1, 10, 10], [20, 1, 10, 10]]},
        "width": 200,
        "height": 300,
        "questions_detected": 1,
        "choices_per_question": 2,
    }
    data = {
        "title": "Mini Quiz",
        "question_count": "1",
        "choice_count": "2",
        "answer_style": "ALPHABETIC",
        "blank_template": (BytesIO(b"fake-image"), "template.png"),
        "answer_key_csv": (BytesIO(b"test_id,Q1\nT1,A\n"), "key.csv"),
    }
    response = client.post(
        "/api/tests/",
        data=data,
        content_type="multipart/form-data",
        headers=auth_headers,
    )
    assert response.status_code == 201, response.get_json()
    body = response.get_json()
    assert body["status"] == "ACTIVE"
    assert body["question_count"] == 1


@patch("app.routes.submissions.evaluate_sheet")
def test_student_submission(evaluate_sheet, client, auth_headers, app):
    with app.app_context():
        from app.models import User

        teacher = User.query.filter_by(email="ada@school.edu").first()
        test = Test(
            test_code="TEST-DEMO",
            teacher_id=teacher.id,
            title="Demo",
            question_count=1,
            choice_count=2,
            answer_style="NUMERIC",
            layout_json={"1": [[0, 0, 10, 10], [12, 0, 10, 10]]},
            template_width=100,
            template_height=100,
            status="ACTIVE",
        )
        db.session.add(test)
        db.session.flush()
        db.session.add(Question(test_id=test.id, question_number=1, correct_position=1))
        db.session.commit()

    evaluate_sheet.return_value = [
        {
            "question_id": 1,
            "question_number": 1,
            "detected_position": 1,
            "correct_position": 1,
            "fill_scores": [0.9, 0.1],
            "confidence": 0.9,
            "status": "CORRECT",
        }
    ]
    response = client.post(
        "/api/tests/TEST-DEMO/submissions",
        data={
            "student_id": "ST001",
            "student_name": "Sam",
            "sheet": (BytesIO(b"fake-sheet"), "sheet.png"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201, response.get_json()
    body = response.get_json()
    assert body["score"] == 1
    assert body["questions"][0]["status"] == "CORRECT"
    assert body["questions"][0]["detected_label"] == "1"
