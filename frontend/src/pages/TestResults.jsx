import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";

function StatusBadge({ status }) {
  const map = {
    COMPLETED: "badge-completed",
    REVIEW_REQUIRED: "badge-review",
    CORRECT: "badge-correct",
    INCORRECT: "badge-danger",
  };
  return <span className={`badge ${map[status] ?? "badge-draft"}`}>{status}</span>;
}

export default function TestResults() {
  const { testId } = useParams();
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api(`/tests/${testId}/results`)
      .then((data) => { setRows(data); setLoading(false); })
      .catch((err) => { setError(err.message); setLoading(false); });
  }, [testId]);

  const avgPct = rows.length
    ? Math.round(rows.reduce((s, r) => s + (r.percentage || 0), 0) / rows.length)
    : null;

  return (
    <section style={{ display: "grid", gap: "1.5rem" }}>
      {/* Header */}
      <div className="row-between">
        <div>
          <Link className="btn sm" to={`/teacher/tests/${testId}`} style={{ marginBottom: "0.75rem", display: "inline-flex" }}>
            ← Back to test
          </Link>
          <h1>Submissions</h1>
          <p className="muted">
            Test code: <code style={{ fontFamily: "monospace", background: "var(--surface-2)", padding: "0.15rem 0.5rem", borderRadius: 4 }}>{testId}</code>
          </p>
        </div>
      </div>

      {/* Quick stats */}
      {rows.length > 0 && (
        <div className="stats">
          <div className="stat">
            <div className="stat-label">Total submissions</div>
            <div className="stat-value">{rows.length}</div>
          </div>
          <div className="stat">
            <div className="stat-label">Average score</div>
            <div className="stat-value">{avgPct}%</div>
          </div>
          <div className="stat">
            <div className="stat-label">Needs review</div>
            <div className="stat-value" style={{ color: "var(--warn)" }}>
              {rows.filter((r) => r.status === "REVIEW_REQUIRED").length}
            </div>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="card" style={{ padding: "1.5rem" }}>
        {error && <p className="alert alert-error">{error}</p>}
        {loading && (
          <div style={{ textAlign: "center", padding: "2rem" }}>
            <span className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
          </div>
        )}

        {!loading && rows.length === 0 && !error && (
          <div style={{ textAlign: "center", padding: "2.5rem 0" }}>
            <p style={{ fontSize: "2rem" }}>📭</p>
            <p className="muted" style={{ marginTop: "0.5rem" }}>No submissions yet for this test.</p>
            <p className="muted" style={{ fontSize: "0.85rem" }}>
              Share the test code with your students so they can upload their sheets at <strong>/submit</strong>.
            </p>
          </div>
        )}

        {!loading && rows.length > 0 && (
          <div className="table-wrap" style={{ margin: 0 }}>
            <table>
              <thead>
                <tr>
                  <th>Student ID</th>
                  <th>Name</th>
                  <th>Score</th>
                  <th>%</th>
                  <th>Correct</th>
                  <th>Submitted</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.submission_id}>
                    <td style={{ fontFamily: "monospace", fontSize: "0.85rem" }}>{row.student_id}</td>
                    <td style={{ fontWeight: 500 }}>{row.student_name}</td>
                    <td style={{ fontWeight: 600 }}>{row.score}/{row.total}</td>
                    <td>
                      <span
                        style={{
                          fontWeight: 700,
                          color: row.percentage >= 75
                            ? "var(--ok)"
                            : row.percentage >= 50
                            ? "var(--warn)"
                            : "var(--danger)",
                        }}
                      >
                        {Math.round(row.percentage)}%
                      </span>
                    </td>
                    <td className="muted">{row.correct_count}</td>
                    <td className="muted" style={{ fontSize: "0.8rem", whiteSpace: "nowrap" }}>
                      {row.submitted_at
                        ? new Date(row.submitted_at).toLocaleString(undefined, { dateStyle: "short", timeStyle: "short" })
                        : "—"}
                    </td>
                    <td><StatusBadge status={row.status} /></td>
                    <td>
                      <Link className="btn sm" to={`/results/${row.submission_id}`}>
                        Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
