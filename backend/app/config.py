import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _database_uri():
    url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/snapscore")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-must-be-at-least-32-chars-long!")
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        os.getenv("SECRET_KEY", "dev-jwt-secret-key-must-be-at-least-32-chars-long!"),
    )
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "8")) * 1024 * 1024
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    MARK_THRESHOLD = float(os.getenv("MARK_THRESHOLD", "0.35"))
    REVIEW_MARGIN = float(os.getenv("REVIEW_MARGIN", "0.08"))
    JWT_ACCESS_TOKEN_EXPIRES = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret-key-must-be-at-least-32-chars-long!"
    SECRET_KEY = "test-secret-key-must-be-at-least-32-chars-long!"
    UPLOAD_FOLDER = str(BASE_DIR / "uploads_test")
