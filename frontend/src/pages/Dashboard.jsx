import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [tests, setTests] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api("/dashboard"), api("/tests/")])
      .then(([dash, list]) => {
        setSummary(dash);
        setTests(list);
      })
      .catch((err) => setError(err.message));
  }, []);

  return (
    <section>
      <div className="row-between">
        <div>
          <h1>Teacher dashboard</h1>
          <p className="muted">Signed in as {user?.name}</p>
        </div>
        <Link className="btn primary" to="/teacher/tests/new">
          Create test
        </Link>
      </div>
      {error && <p className="error">{error}</p>}
      {summary && (
        <div className="stats">
          <div className="stat">
            <span>Total tests</span>
            <strong>{summary.total_tests}</strong>
          </div>
          <div className="stat">
            <span>Active tests</span>
            <strong>{summary.active_tests}</strong>
          </div>
          <div className="stat">
            <span>Submissions</span>
            <strong>{summary.total_submissions}</strong>
          </div>
        </div>
      )}
      <h2>Your tests</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Test ID</th>
              <th>Questions</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {tests.map((test) => (
              <tr key={test.id}>
                <td>
                  <Link to={`/teacher/tests/${test.test_code}`}>{test.title}</Link>
                </td>
                <td>{test.test_code}</td>
                <td>{test.question_count}</td>
                <td>{test.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h2>Recent results</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Student</th>
              <th>Test</th>
              <th>Score</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {(summary?.recent_results || []).map((item) => (
              <tr key={item.submission_id}>
                <td>
                  <Link to={`/results/${item.submission_id}`}>{item.student_name}</Link>
                </td>
                <td>{item.test_id}</td>
                <td>
                  {item.score}/{item.total} ({item.percentage}%)
                </td>
                <td>{item.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
