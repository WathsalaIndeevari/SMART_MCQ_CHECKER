# SnapScore – Smart MCQ Checker

Web-based OMR grading: teachers upload a blank bubble sheet and CSV answer key; students upload a photo of a filled sheet; OpenCV scores it.

## Local setup

### Backend

1. Create a PostgreSQL database named `snapscore`.
2. From `backend/`:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
flask --app wsgi db upgrade
python run.py
```

If you skip migrations, the test suite uses an in-memory SQLite database. For a first local run without Alembic:

```bash
python -c "from run import app; from app.extensions import db; app.app_context().push(); db.create_all()"
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:5000`.

## Deploy (Render)

`render.yaml` defines a web service and Postgres. Set `FRONTEND_URL` to the static site origin. Uploaded images live on local disk; Render’s free filesystem is ephemeral unless you add a disk.

## Demo CSV

```csv
test_id,Q1,Q2,Q3,Q4,Q5
Math_Test_01,A,C,B,D,A
```
