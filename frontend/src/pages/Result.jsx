import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { api, downloadUrl } from "../api";

function statusBadge(status) {
  if (!status) return null;
  const cls = `badge badge-${status.toLowerCase()}`;
  const labels = {
    CORRECT: "✓ Correct",
    INCORRECT: "✗ Incorrect",
    UNANSWERED: "— Unanswered",
    MULTIPLE: "⚠ Multiple",
    REVIEW_REQUIRED: "👁 Review",
    COMPLETED: "✓ Completed",
    REVIEW_REQUIRED_SUB: "👁 Review required",
  };
  return <span className={cls}>{labels[status] ?? status}</span>;
}

function ScoreRing({ percentage }) {
  const pct = Math.round(percentage ?? 0);
  const color =
    pct >= 75 ? "var(--ok)" : pct >= 50 ? "var(--warn)" : "var(--danger)";

  return (
    <div style={{ textAlign: "center" }}>
      <div
        style={{
          width: 96,
          height: 96,
          borderRadius: "50%",
          border: `6px solid ${color}`,
          display: "grid",
          placeItems: "center",
          margin: "0 auto 0.4rem",
          boxShadow: `0 0 20px ${color}44`,
        }}
      >
        <span style={{ fontSize: "1.5rem", fontWeight: 800, color }}>
          {pct}%
        </span>
      </div>
      <span className="muted" style={{ fontSize: "0.78rem" }}>percentage</span>
    </div>
  );
}

export default function Result() {
  const { submissionId } = useParams();
  const location = useLocation();
  const [result, setResult] = useState(location.state || null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (result) return;
    api(`/submissions/${submissionId}/results`)
      .then(setResult)
      .catch((err) => setError(err.message));
  }, [submissionId, result]);

  if (error)
    return (
      <div className="card narrow" style={{ margin: "0 auto" }}>
        <p className="alert alert-error">{error}</p>
        <Link className="btn" to="/submit" style={{ marginTop: "1rem" }}>
          ← Try again
        </Link>
      </div>
    );

  if (!result)
    return (
      <div className="card" style={{ textAlign: "center" }}>
        <span className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
        <p className="muted" style={{ marginTop: "0.75rem" }}>Loading result…</p>
      </div>
    );

  const subStatus = result.status === "REVIEW_REQUIRED" ? "REVIEW_REQUIRED_SUB" : result.status;

  return (
    <section style={{ display: "grid", gap: "1.5rem" }}>
      {/* Header */}
      <div className="card">
        <div className="row-between">
          <div>
            <p className="muted" style={{ fontSize: "0.8rem", marginBottom: "0.35rem" }}>
              Result for {result.test_name || `Test ${result.test_id}`}
            </p>
            <h1>{result.student_name}</h1>
            <p className="muted">{result.student_id}</p>
          </div>
          <ScoreRing percentage={result.percentage} />
        </div>

        {result.status === "REVIEW_REQUIRED" && (
          <div className="alert alert-warn" style={{ marginTop: "1rem" }}>
            ⚠️ Some answers were ambiguous and flagged for teacher review. Your displayed score may change.
          </div>
        )}

        {/* Stats */}
        <div className="stats" style={{ marginTop: "1.25rem" }}>
          <div className="stat">
            <div className="stat-label">Score</div>
            <div className="stat-value">{result.score}<span style={{ fontSize: "1rem", color: "var(--text-dim)" }}>/{result.total}</span></div>
          </div>
          <div className="stat">
            <div className="stat-label">Correct</div>
            <div className="stat-value" style={{ color: "var(--ok)" }}>{result.correct_count}</div>
          </div>
          <div className="stat">
            <div className="stat-label">Incorrect</div>
            <div className="stat-value" style={{ color: "var(--danger)" }}>{result.incorrect_count}</div>
          </div>
          <div className="stat">
            <div className="stat-label">Unanswered</div>
            <div className="stat-value">{result.unanswered_count}</div>
          </div>
          {result.multiple_count > 0 && (
            <div className="stat">
              <div className="stat-label">Multi-marked</div>
              <div className="stat-value" style={{ color: "var(--warn)" }}>{result.multiple_count}</div>
            </div>
          )}
          <div className="stat">
            <div className="stat-label">Status</div>
            <div style={{ marginTop: "0.4rem" }}>{statusBadge(subStatus)}</div>
          </div>
        </div>

        <div className="actions" style={{ marginTop: "1rem" }}>
          <a
            id="download-csv-btn"
            className="btn"
            href={downloadUrl(`/submissions/${result.submission_id}/download`)}
          >
            ⬇ Download CSV report
          </a>
          <Link className="btn" to="/submit">
            ← Submit another sheet
          </Link>
        </div>
      </div>

      {/* Per-question table */}
      <div className="card">
        <h2 style={{ marginBottom: "0.75rem" }}>Question breakdown</h2>
        <div className="table-wrap" style={{ margin: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Q#</th>
                <th>Your answer</th>
                <th>Correct answer</th>
                <th>Status</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {(result.questions || []).map((row) => (
                <tr key={row.question_number}>
                  <td style={{ fontWeight: 600, color: "var(--text-head)" }}>
                    {row.question_number}
                  </td>
                  <td style={{ fontFamily: "monospace", fontWeight: 600 }}>
                    {row.detected_label ?? "—"}
                  </td>
                  <td style={{ fontFamily: "monospace" }}>{row.correct_label}</td>
                  <td>{statusBadge(row.status)}</td>
                  <td className="muted">
                    {row.confidence != null
                      ? `${Math.round(row.confidence * 100)}%`
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
