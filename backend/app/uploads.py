import secrets
import string
from pathlib import Path

from werkzeug.utils import secure_filename

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
CSV_EXTENSIONS = {".csv"}


def generate_test_code():
    from app.models import Test

    alphabet = string.ascii_uppercase + string.digits
    for _ in range(12):
        suffix = "".join(secrets.choice(alphabet) for _ in range(4))
        code = f"TEST-{suffix}"
        if Test.query.filter_by(test_code=code).first() is None:
            return code
    return f"TEST-{secrets.token_hex(4).upper()}"


def allowed_image(filename):
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS


def allowed_csv(filename):
    return Path(filename).suffix.lower() in CSV_EXTENSIONS


def save_upload(file_storage, dest_dir, prefix="file"):
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    original = secure_filename(file_storage.filename or "upload")
    suffix = Path(original).suffix.lower() or ".bin"
    name = f"{prefix}_{secrets.token_hex(8)}{suffix}"
    path = dest / name
    file_storage.save(str(path))
    return str(path)
