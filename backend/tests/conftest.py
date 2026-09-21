import pytest

from app import create_app
from app.config import TestingConfig
from app.extensions import db


@pytest.fixture()
def app():
    application = create_app(TestingConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Ada Teacher",
            "email": "ada@school.edu",
            "password": "secret123",
        },
    )
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
