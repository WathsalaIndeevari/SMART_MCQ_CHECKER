import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

export default function CreateTest() {
  const navigate = useNavigate();
  const templateRef = useRef(null);
  const csvRef = useRef(null);

  const [form, setForm] = useState({
    title: "",
    question_count: 10,
    choice_count: 4,
    answer_style: "ALPHABETIC",
  });
  const [template, setTemplate] = useState(null);
  const [csv, setCsv] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function field(key) {
    return (e) => setForm({ ...form, [key]: e.target.value });
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError(""); setMessage("");
    const data = new FormData();
    data.append("title", form.title);
    data.append("question_count", String(form.question_count));
    data.append("choice_count", String(form.choice_count));
    data.append("answer_style", form.answer_style);
    if (template) data.append("blank_template", template);
    if (csv) data.append("answer_key_csv", csv);
    setBusy(true);
    try {
      const created = await api("/tests/", { method: "POST", body: data });
      navigate(`/teacher/tests/${created.test_code}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <div className="card" style={{ maxWidth: 680, margin: "0 auto" }}>
        <div style={{ marginBottom: "1.75rem" }}>
          <h1>Create a new test</h1>
          <p className="muted">
            You can save as a draft and upload the template and answer key later.
          </p>
        </div>

        <form id="create-test-form" className="form" onSubmit={onSubmit}>
          {/* Title */}
          <label>
            Test title <span className="hint">(required)</span>
            <input
              id="test-title"
              required
              value={form.title}
              onChange={field("title")}
              placeholder="e.g. Biology 101 Midterm"
            />
          </label>

          {/* Q count + choice count */}
          <div className="grid-2">
            <label>
              Number of questions
              <input
                id="question-count"
                type="number"
                min="1"
                max="200"
                required
                value={form.question_count}
                onChange={field("question_count")}
              />
            </label>
            <label>
              Choices per question
              <input
                id="choice-count"
                type="number"
                min="2"
                max="5"
                required
                value={form.choice_count}
                onChange={field("choice_count")}
              />
            </label>
          </div>

          {/* Answer style */}
          <label>
            Answer label style
            <select id="answer-style" value={form.answer_style} onChange={field("answer_style")}>
              <option value="ALPHABETIC">Alphabetic — A, B, C, D, E</option>
              <option value="NUMERIC">Numeric — 1, 2, 3, 4, 5</option>
            </select>
          </label>

          <hr className="divider" />
          <p className="muted" style={{ fontSize: "0.85rem", marginTop: "-0.5rem" }}>
            Optional — skip if uploading later from the test details page.
          </p>

          {/* Template upload */}
          <label className="dropzone-label">
            Blank OMR template <span className="hint">(JPG/PNG)</span>
            <input
              id="template-upload"
              ref={templateRef}
              type="file"
              accept=".jpg,.jpeg,.png"
              style={{ display: "none" }}
              onChange={(e) => setTemplate(e.target.files[0] || null)}
            />
            <div
              className={`dropzone${template ? " has-file" : ""}`}
              onClick={() => templateRef.current?.click()}
            >
              {template ? (
                <>
                  <div className="dz-icon">✅</div>
                  <div className="dz-text">{template.name}</div>
                  <div className="dz-sub">Click to change</div>
                </>
              ) : (
                <>
                  <div className="dz-icon">🖼️</div>
                  <div className="dz-text">Click to upload blank template</div>
                  <div className="dz-sub">Bubbles will be detected automatically</div>
                </>
              )}
            </div>
          </label>

          {/* CSV upload */}
          <label className="dropzone-label">
            Answer key CSV <span className="hint">(.csv)</span>
            <input
              id="csv-upload"
              ref={csvRef}
              type="file"
              accept=".csv"
              style={{ display: "none" }}
              onChange={(e) => setCsv(e.target.files[0] || null)}
            />
            <div
              className={`dropzone${csv ? " has-file" : ""}`}
              onClick={() => csvRef.current?.click()}
            >
              {csv ? (
                <>
                  <div className="dz-icon">✅</div>
                  <div className="dz-text">{csv.name}</div>
                  <div className="dz-sub">Click to change</div>
                </>
              ) : (
                <>
                  <div className="dz-icon">📊</div>
                  <div className="dz-text">Click to upload answer key</div>
                  <div className="dz-sub">Format: test_id,Q1,Q2,… with A–E or 1–5 answers</div>
                </>
              )}
            </div>
          </label>

          {error && <p className="alert alert-error">{error}</p>}
          {message && <p className="alert alert-ok">{message}</p>}

          <div className="actions">
            <button id="save-test-btn" className="btn primary lg" type="submit" disabled={busy}>
              {busy ? (
                <><span className="spinner" /> Processing…</>
              ) : (
                "Save test"
              )}
            </button>
            <a className="btn" href="/teacher">Cancel</a>
          </div>
        </form>
      </div>
    </section>
  );
}
