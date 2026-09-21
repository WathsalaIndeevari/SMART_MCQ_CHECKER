import { useRef, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { position_to_label_client } from "../labels";

function StatusBadge({ status }) {
  const map = {
    ACTIVE: "badge-active",
    DRAFT: "badge-draft",
    CLOSED: "badge-closed",
  };
  return <span className={`badge ${map[status] ?? "badge-draft"}`}>{status}</span>;
}

export default function TestDetails() {
  const { testId } = useParams();
  const templateRef = useRef(null);
  const csvRef = useRef(null);
  const [test, setTest] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState("");

  async function load() {
    const data = await api(`/tests/${testId}`);
    setTest(data);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, [testId]);

  async function upload(kind, file) {
    if (!file) return;
    setError(""); setMessage(""); setBusy(kind);
    const data = new FormData();
    try {
      if (kind === "template") {
        data.append("blank_template", file);
        const res = await api(`/tests/${testId}/template`, { method: "POST", body: data });
        setMessage(res.message || "Template processed successfully.");
      } else {
        data.append("answer_key_csv", file);
        await api(`/tests/${testId}/answer-key`, { method: "POST", body: data });
        setMessage("Answer key saved successfully.");
      }
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy("");
    }
  }

  async function setStatus(status) {
    setError(""); setMessage("");
    try {
      const updated = await api(`/tests/${testId}`, { method: "PUT", body: { status } });
      setTest(updated);
    } catch (err) {
      setError(err.message);
    }
  }

  if (!test)
    return (
      <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
        {error ? (
          <p className="alert alert-error">{error}</p>
        ) : (
          <>
            <span className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
            <p className="muted" style={{ marginTop: "0.75rem" }}>Loading test…</p>
          </>
        )}
      </div>
    );

  const layoutCount = test.layout_json ? Object.keys(test.layout_json).length : 0;
  const hasTemplate = !!test.layout_json;
  const hasKey = test.answer_key?.length > 0;

  return (
    <section style={{ display: "grid", gap: "1.5rem" }}>
      {/* Header card */}
      <div className="card">
        <div className="row-between">
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.5rem" }}>
              <h1 style={{ margin: 0 }}>{test.title}</h1>
              <StatusBadge status={test.status} />
            </div>
            <p className="muted" style={{ fontSize: "0.875rem" }}>
              Code: <code style={{ fontFamily: "monospace", background: "var(--surface-2)", padding: "0.15rem 0.5rem", borderRadius: 4 }}>{test.test_code}</code>
              &nbsp;·&nbsp; {test.question_count} questions
              &nbsp;·&nbsp; {test.choice_count} choices
              &nbsp;·&nbsp; {test.answer_style}
            </p>
          </div>
          <Link className="btn" to={`/teacher/tests/${test.test_code}/results`}>
            View submissions →
          </Link>
        </div>

        {/* Readiness checklist */}
        <div style={{ display: "flex", gap: "0.75rem", margin: "1.25rem 0 0", flexWrap: "wrap" }}>
          <span className={`badge ${hasTemplate ? "badge-correct" : "badge-draft"}`}>
            {hasTemplate ? "✓ Template detected" : "○ No template"}
          </span>
          <span className={`badge ${hasKey ? "badge-correct" : "badge-draft"}`}>
            {hasKey ? "✓ Answer key loaded" : "○ No answer key"}
          </span>
          {layoutCount > 0 && (
            <span className="badge badge-info">{layoutCount} questions detected</span>
          )}
        </div>

        {/* Alerts */}
        {error && <p className="alert alert-error" style={{ marginTop: "1rem" }}>{error}</p>}
        {message && <p className="alert alert-ok" style={{ marginTop: "1rem" }}>{message}</p>}

        {/* Status actions */}
        <div className="actions" style={{ marginTop: "1rem" }}>
          {test.status === "DRAFT" && (
            <button
              id="activate-btn"
              className="btn primary"
              onClick={() => setStatus("ACTIVE")}
              disabled={!hasTemplate || !hasKey}
              title={!hasTemplate || !hasKey ? "Upload template and answer key first" : ""}
            >
              ▶ Activate test
            </button>
          )}
          {test.status === "ACTIVE" && (
            <button id="close-btn" className="btn danger" onClick={() => setStatus("CLOSED")}>
              ✕ Close test
            </button>
          )}
          {test.status === "CLOSED" && (
            <button className="btn" onClick={() => setStatus("ACTIVE")}>
              ↺ Re-open test
            </button>
          )}
        </div>
      </div>

      {/* Template section */}
      <div className="card">
        <h2 style={{ marginBottom: "1rem" }}>📷 OMR Template</h2>

        {test.template_path && (
          <img
            className="preview-img"
            src={`/api/tests/${test.test_code}/template-file`}
            alt="Blank OMR template"
            style={{ marginBottom: "1rem" }}
          />
        )}

        <p className="muted" style={{ marginBottom: "1rem", fontSize: "0.875rem" }}>
          {hasTemplate
            ? `Detected ${layoutCount} of ${test.question_count} questions.`
            : "Upload the blank (unfilled) bubble sheet so SnapScore can learn the layout."}
        </p>

        <input
          id="replace-template"
          ref={templateRef}
          type="file"
          accept=".jpg,.jpeg,.png"
          style={{ display: "none" }}
          onChange={(e) => upload("template", e.target.files[0])}
        />
        <button
          className="btn"
          onClick={() => templateRef.current?.click()}
          disabled={busy === "template"}
        >
          {busy === "template" ? <><span className="spinner" /> Detecting bubbles…</> : hasTemplate ? "⬆ Replace template" : "⬆ Upload template"}
        </button>
      </div>

      {/* Answer key section */}
      <div className="card">
        <h2 style={{ marginBottom: "1rem" }}>🗝️ Answer Key</h2>

        {hasKey ? (
          <>
            <p className="muted" style={{ marginBottom: "0.75rem", fontSize: "0.875rem" }}>
              {test.answer_key.length} answers loaded. Click any question to see details.
            </p>
            <ul className="key-list">
              {test.answer_key.map((item) => (
                <li key={item.question_number}>
                  <span style={{ color: "var(--text-dim)" }}>Q{item.question_number}</span>
                  &nbsp;
                  <strong>{position_to_label_client(item.correct_position, test.answer_style)}</strong>
                </li>
              ))}
            </ul>
          </>
        ) : (
          <p className="muted" style={{ marginBottom: "1rem", fontSize: "0.875rem" }}>
            Upload a CSV with format: <code style={{ fontFamily: "monospace" }}>test_id,Q1,Q2,…</code>
          </p>
        )}

        <input
          id="replace-csv"
          ref={csvRef}
          type="file"
          accept=".csv"
          style={{ display: "none", marginTop: "1rem" }}
          onChange={(e) => upload("csv", e.target.files[0])}
        />
        <button
          className="btn"
          style={{ marginTop: "1rem" }}
          onClick={() => csvRef.current?.click()}
          disabled={busy === "csv"}
        >
          {busy === "csv" ? <><span className="spinner" /> Parsing CSV…</> : hasKey ? "⬆ Replace answer key" : "⬆ Upload answer key CSV"}
        </button>
      </div>
    </section>
  );
}
