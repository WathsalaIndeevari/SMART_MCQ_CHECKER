import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const TIPS = [
  "Lay the sheet flat — avoid folding or crumpling",
  "Use even lighting; avoid harsh shadows",
  "Capture the full page including all four edges",
  "Hold steady for a sharp photo (portrait orientation)",
];

export default function SubmitSheet() {
  const navigate = useNavigate();
  const fileRef = useRef(null);

  const [form, setForm] = useState({ test_id: "", student_id: "", student_name: "" });
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function onFile(e) {
    const f = e.target.files?.[0];
    setFile(f || null);
    setPreview(f ? URL.createObjectURL(f) : "");
  }

  function field(key) {
    return (e) => setForm({ ...form, [key]: e.target.value });
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    if (!file) { setError("Please attach a JPG or PNG of the completed answer sheet."); return; }

    const data = new FormData();
    data.append("student_id", form.student_id);
    data.append("student_name", form.student_name);
    data.append("sheet", file);

    setBusy(true);
    try {
      const result = await api(`/tests/${encodeURIComponent(form.test_id)}/submissions`, {
        method: "POST",
        body: data,
      });
      navigate(`/results/${result.submission_id}`, { state: result });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <div className="card" style={{ maxWidth: 640, margin: "0 auto" }}>
        <h1 style={{ marginBottom: "0.35rem" }}>Submit answer sheet</h1>
        <p className="muted" style={{ marginBottom: "1.5rem" }}>
          Enter the test code your teacher shared, then upload a photo of your completed sheet.
        </p>

        <form className="form" onSubmit={onSubmit} id="submit-form">
          {/* Test ID */}
          <label>
            Test code
            <input
              id="test_id"
              required
              autoComplete="off"
              value={form.test_id}
              onChange={field("test_id")}
              placeholder="e.g. TEST-A3K9"
            />
          </label>

          {/* Student fields */}
          <div className="grid-2">
            <label>
              Student ID
              <input
                id="student_id"
                required
                value={form.student_id}
                onChange={field("student_id")}
                placeholder="e.g. ST001"
              />
            </label>
            <label>
              Full name
              <input
                id="student_name"
                required
                value={form.student_name}
                onChange={field("student_name")}
                placeholder="e.g. Alex Johnson"
              />
            </label>
          </div>

          {/* File dropzone */}
          <label className="dropzone-label">
            <span style={{ display: "block", fontWeight: 600, fontSize: "0.875rem", color: "var(--text-head)", marginBottom: "0.4rem" }}>
              Answer sheet photo
            </span>
            <input
              id="sheet_upload"
              ref={fileRef}
              type="file"
              accept=".jpg,.jpeg,.png"
              style={{ display: "none" }}
              onChange={onFile}
            />
            <div
              className={`dropzone${file ? " has-file" : ""}`}
              onClick={() => fileRef.current?.click()}
            >
              {file ? (
                <>
                  <div className="dz-icon">✅</div>
                  <div className="dz-text">{file.name}</div>
                  <div className="dz-sub">Click to change</div>
                </>
              ) : (
                <>
                  <div className="dz-icon">📄</div>
                  <div className="dz-text">Click to select a photo</div>
                  <div className="dz-sub">JPG, JPEG, or PNG · Max 8 MB</div>
                </>
              )}
            </div>
          </label>

          {preview && (
            <img className="preview-img" src={preview} alt="Answer sheet preview" />
          )}

          {/* Photo tips */}
          <div className="alert alert-info" style={{ marginTop: "0.25rem" }}>
            <strong>📸 Tips for best results:</strong>
            <ul style={{ margin: "0.4rem 0 0 1.1rem", lineHeight: 1.7 }}>
              {TIPS.map((t) => <li key={t}>{t}</li>)}
            </ul>
          </div>

          {error && <p className="alert alert-error">{error}</p>}

          <button id="submit-btn" className="btn primary lg" type="submit" disabled={busy} style={{ marginTop: "0.5rem" }}>
            {busy ? (
              <><span className="spinner" /> Evaluating your sheet…</>
            ) : (
              "Submit for evaluation →"
            )}
          </button>
        </form>
      </div>
    </section>
  );
}
