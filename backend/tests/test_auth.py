from datetime import timedelta

from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import Test, User


def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Jane Teacher", "email": "jane@school.org", "password": "securepassword"},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert "access_token" in body
    assert body["user"]["name"] == "Jane Teacher"
    assert body["user"]["email"] == "jane@school.org"
    assert body["user"]["role"] == "TEACHER"
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_register_missing_fields(client):
    # Missing password
    res1 = client.post(
        "/api/auth/register",
        json={"name": "No Password", "email": "nopass@school.org"},
    )
    assert res1.status_code == 400
    assert res1.get_json()["error"] == "Name, email, and password are required."

    # Missing email
    res2 = client.post(
        "/api/auth/register",
        json={"name": "No Email", "password": "securepassword"},
    )
    assert res2.status_code == 400
    assert res2.get_json()["error"] == "Name, email, and password are required."

    # Empty payload
    res3 = client.post("/api/auth/register", json={})
    assert res3.status_code == 400
    assert res3.get_json()["error"] == "Name, email, and password are required."


def test_register_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Short Pass", "email": "short@school.org", "password": "12345"},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Password must be at least 6 characters."


def test_register_duplicate_email(client):
    payload = {"name": "First User", "email": "duplicate@school.org", "password": "password123"}
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 409
    assert res2.get_json()["error"] == "An account with this email already exists."


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={"name": "Login User", "email": "login@school.org", "password": "correctpassword"},
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "login@school.org", "password": "correctpassword"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert "access_token" in body
    assert body["user"]["email"] == "login@school.org"


def test_login_missing_fields(client):
    res1 = client.post("/api/auth/login", json={"email": "only@school.org"})
    assert res1.status_code == 400
    assert res1.get_json()["error"] == "Email and password are required."

    res2 = client.post("/api/auth/login", json={})
    assert res2.status_code == 400
    assert res2.get_json()["error"] == "Email and password are required."


def test_login_invalid_credentials(client):
    # Non-existent user
    res1 = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@school.org", "password": "anypassword"},
    )
    assert res1.status_code == 401
    assert res1.get_json()["error"] == "Invalid email or password."

    # Incorrect password
    client.post(
        "/api/auth/register",
        json={"name": "Teacher A", "email": "teachera@school.org", "password": "correctpassword"},
    )
    res2 = client.post(
        "/api/auth/login",
        json={"email": "teachera@school.org", "password": "wrongpassword"},
    )
    assert res2.status_code == 401
    assert res2.get_json()["error"] == "Invalid email or password."


def test_me_endpoint_and_token_errors(client):
    # Missing token -> 401 Authentication required
    res_no_token = client.get("/api/auth/me")
    assert res_no_token.status_code == 401
    assert res_no_token.get_json()["error"] == "Authentication required."

    # Invalid token -> 401 Invalid or expired token
    res_invalid_token = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not-a-valid-token"}
    )
    assert res_invalid_token.status_code == 401
    assert res_invalid_token.get_json()["error"] == "Invalid or expired token."

    # Expired token -> 401 Invalid or expired token
    with client.application.app_context():
        expired_token = create_access_token(
            identity="1", expires_delta=timedelta(seconds=-10)
        )
    res_expired = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert res_expired.status_code == 401
    assert res_expired.get_json()["error"] == "Invalid or expired token."


def test_teacher_role_required_guard(client, app):
    # Create a non-teacher (e.g. STUDENT)
    with app.app_context():
        student = User(name="Student Bob", email="student@school.org", role="STUDENT")
        student.set_password("studentpass")
        db.session.add(student)
        db.session.commit()
        student_id = student.id

    with app.app_context():
        student_token = create_access_token(identity=str(student_id))

    headers = {"Authorization": f"Bearer {student_token}"}

    # Student cannot access /api/dashboard
    res_dash = client.get("/api/dashboard", headers=headers)
    assert res_dash.status_code == 403
    assert res_dash.get_json()["error"] == "Teacher access required."

    # Student cannot create test
    res_create = client.post("/api/tests/", data={"title": "Quiz"}, headers=headers)
    assert res_create.status_code == 403
    assert res_create.get_json()["error"] == "Teacher access required."

    # Student cannot list tests
    res_list = client.get("/api/tests/", headers=headers)
    assert res_list.status_code == 403
    assert res_list.get_json()["error"] == "Teacher access required."


def test_ownership_isolation(client, app):
    # Register Teacher A
    res_a = client.post(
        "/api/auth/register",
        json={"name": "Teacher A", "email": "ta@school.org", "password": "password123"},
    )
    token_a = res_a.get_json()["access_token"]
    teacher_a_id = res_a.get_json()["user"]["id"]

    # Register Teacher B
    res_b = client.post(
        "/api/auth/register",
        json={"name": "Teacher B", "email": "tb@school.org", "password": "password123"},
    )
    token_b = res_b.get_json()["access_token"]

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Teacher A creates a test directly in DB
    with app.app_context():
        test_a = Test(
            test_code="TEST-AAA1",
            teacher_id=teacher_a_id,
            title="Teacher A Quiz",
            question_count=5,
            choice_count=4,
            answer_style="ALPHABETIC",
            status="DRAFT",
        )
        db.session.add(test_a)
        db.session.commit()
        test_id = test_a.id

    # Teacher A can access the test
    get_a = client.get(f"/api/tests/{test_id}", headers=headers_a)
    assert get_a.status_code == 200
    assert get_a.get_json()["title"] == "Teacher A Quiz"

    # Teacher B CANNOT view Teacher A's test
    get_b = client.get(f"/api/tests/{test_id}", headers=headers_b)
    assert get_b.status_code == 403
    assert get_b.get_json()["error"] == "You can only manage tests you created."

    # Teacher B CANNOT update Teacher A's test
    put_b = client.put(
        f"/api/tests/{test_id}",
        json={"title": "Hacked Title"},
        headers=headers_b,
    )
    assert put_b.status_code == 403
    assert put_b.get_json()["error"] == "You can only manage tests you created."

    # Teacher B CANNOT delete Teacher A's test
    del_b = client.delete(f"/api/tests/{test_id}", headers=headers_b)
    assert del_b.status_code == 403
    assert del_b.get_json()["error"] == "You can only manage tests you created."

    # Teacher B CANNOT view submissions for Teacher A's test
    sub_b = client.get(f"/api/tests/{test_id}/submissions", headers=headers_b)
    assert sub_b.status_code == 403
    assert sub_b.get_json()["error"] == "You can only manage tests you created."

    # Teacher A querying a non-existent test gets 404
    get_404 = client.get("/api/tests/999999", headers=headers_a)
    assert get_404.status_code == 404
    assert get_404.get_json()["error"] == "Test not found."


def test_public_student_routes_do_not_require_auth(client):
    # Submitting to non-existent test returns 404, not 401
    res_sub = client.post("/api/tests/TEST-NONEXISTENT/submissions")
    assert res_sub.status_code == 404
    assert "Test not found" in res_sub.get_json()["error"]

    # Viewing non-existent submission returns 404, not 401
    res_view = client.get("/api/submissions/999999")
    assert res_view.status_code == 404
    assert res_view.get_json()["error"] == "Submission not found."

    # Downloading non-existent submission returns 404, not 401
    res_dl = client.get("/api/submissions/999999/download")
    assert res_dl.status_code == 404
    assert res_dl.get_json()["error"] == "Submission not found."
