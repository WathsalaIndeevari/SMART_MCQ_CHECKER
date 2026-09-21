from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.extensions import db
from app.models import Test, User


def teacher_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        try:
            user = db.session.get(User, int(user_id)) if user_id is not None else None
        except (ValueError, TypeError):
            user = None
        if not user or user.role != "TEACHER":
            return jsonify({"error": "Teacher access required."}), 403
        return fn(user, *args, **kwargs)

    return wrapper


def get_owned_test(user, test_id):
    test = find_test(test_id)
    if test is None:
        return None, (jsonify({"error": "Test not found."}), 404)
    if test.teacher_id != user.id:
        return None, (jsonify({"error": "You can only manage tests you created."}), 403)
    return test, None


def find_test(test_id):
    if test_id is None:
        return None
    text = str(test_id)
    if text.isdigit():
        test = db.session.get(Test, int(text))
        if test:
            return test
    return Test.query.filter_by(test_code=text).first()
