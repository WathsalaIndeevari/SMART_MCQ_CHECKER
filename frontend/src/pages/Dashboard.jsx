import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../AuthContext";

function StatusBadge({ status }) {
  const map = {
    ACTIVE: "badge-active",
    DRAFT: "badge-draft",
    CLOSED: "badge-closed",
    COMPLETED: "badge-completed",
    REVIEW_REQUIRED: "badge-review",
  };
  return <span className={`badge ${map[status] ?? "badge-draft"}`}>{status}</span>;
}

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [tests, setTests] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api("/dashboard"), api("/tests/")])
      .then(([dash, list]) => { setSummary(dash); setTests(list); })
      .catch((err) => setError(err.message));
  }, []);

  return (
    <section style={{ display: "grid", gap: "1.5rem" }}>
      {/* Header */}
      <div className="row-between">
        <div>
          <h1>Welcome back{user?.name ? `, ${user.name.split(" ")[0]}` : ""}! 👋</h1>
          <p className="muted">{user?.email}</p>
        </div>
        <Link id="create-test-btn" className="btn primary" to="/teacher/tests/new">
          + Create test
        </Link>
      </div>

      {error && <p className="alert alert-error">{error}</p>}

      {/* Stat cards */}
      <div className="stats">
        <div className="stat">
          <div className="stat-label">Total tests</div>
          <div className="stat-value">{summary?.total_tests ?? "—"}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Active tests</div>
          <div className="stat-value" style={{ color: "var(--ok)" }}>
            {summary?.active_tests ?? "—"}
          </div>
          <div className="stat-sub">accepting submissions</div>
        </div>
        <div className="stat">
          <div className="stat-label">Submissions</div>
          <div className="stat-value">{summary?.total_submissions ?? "—"}</div>
          <div className="stat-sub">all time</div>
        </div>
      </div>

      {/* Tests table */}
      <div className="card" style={{ padding: "1.5rem" }}>
        <div className="row-between" style={{ marginBottom: "1rem" }}>
          <h2>Your tests</h2>
          {tests.length > 0 && (
            <Link className="btn sm" to="/teacher/tests/new">+ New</Link>
          )}
        </div>

        {tests.length === 0 ? (
          <div style={{ textAlign: "center", padding: "2rem 0" }}>
            <p style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>📋</p>
            <p className="muted">No tests yet.</p>
            <Link className="btn primary" to="/teacher/tests/new" style={{ marginTop: "1rem", display: "inline-flex" }}>
              Create your first test
            </Link>
          </div>
        ) : (
          <div className="table-wrap" style={{ margin: 0 }}>
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Test code</th>
                  <th>Questions</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {tests.map((test) => (
                  <tr key={test.id}>
                    <td>
                      <Link to={`/teacher/tests/${test.test_code}`} style={{ fontWeight: 600, color: "var(--text-head)" }}>
                        {test.title}
                      </Link>
                    </td>
                    <td>
                      <code style={{ fontFamily: "monospace", background: "var(--surface-2)", padding: "0.15rem 0.4rem", borderRadius: 4, fontSize: "0.8rem" }}>
                        {test.test_code}
                      </code>
                    </td>
                    <td className="muted">{test.question_count}</td>
                    <td><StatusBadge status={test.status} /></td>
                    <td>
                      <Link className="btn sm" to={`/teacher/tests/${test.test_code}`}>
                        Manage →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recent results */}
      {summary?.recent_results?.length > 0 && (
        <div className="card" style={{ padding: "1.5rem" }}>
          <h2 style={{ marginBottom: "1rem" }}>Recent submissions</h2>
          <div className="table-wrap" style={{ margin: 0 }}>
            <table>
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Test</th>
                  <th>Score</th>
                  <th>%</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {summary.recent_results.map((item) => (
                  <tr key={item.submission_id}>
                    <td style={{ fontWeight: 500 }}>{item.student_name}</td>
                    <td className="muted" style={{ fontSize: "0.8rem" }}>{item.test_id}</td>
                    <td>{item.score}/{item.total}</td>
                    <td style={{ fontWeight: 600 }}>{Math.round(item.percentage)}%</td>
                    <td><StatusBadge status={item.status} /></td>
                    <td>
                      <Link className="btn sm" to={`/results/${item.submission_id}`}>
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
