import sys
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from app.config import Config
from app.extensions import cors, db, jwt, migrate

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    upload_root = Path(app.config["UPLOAD_FOLDER"])
    (upload_root / "templates").mkdir(parents=True, exist_ok=True)
    (upload_root / "sheets").mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db, directory=str(ROOT / "migrations"))
    jwt.init_app(app)

    @jwt.unauthorized_loader
    def missing_token(_reason):
        return jsonify({"error": "Authentication required."}), 401

    @jwt.invalid_token_loader
    def invalid_token(_reason):
        return jsonify({"error": "Invalid or expired token."}), 401

    @jwt.expired_token_loader
    def expired_token(_header, _payload):
        return jsonify({"error": "Invalid or expired token."}), 401

    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get("FRONTEND_URL", "*")}},
        supports_credentials=True,
    )

    from app import models  # noqa: F401
    from app.routes.auth import auth_bp
    from app.routes.submissions import submissions_bp
    from app.routes.tests import tests_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tests_bp, url_prefix="/api/tests")
    app.register_blueprint(submissions_bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.errorhandler(413)
    def too_large(_e):
        return jsonify({"error": "File is too large."}), 413

    return app
