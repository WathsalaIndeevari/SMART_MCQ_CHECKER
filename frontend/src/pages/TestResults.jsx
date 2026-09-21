import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";

export default function TestResults() {
  const { testId } = useParams();
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api(`/tests/${testId}/results`)
      .then(setRows)
      .catch((err) => setError(err.message));
  }, [testId]);

  return (
    <section className="card">
      <h1>Submissions</h1>
      {error && <p className="error">{error}</p>}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Student ID</th>
              <th>Name</th>
              <th>Score</th>
              <th>Percentage</th>
              <th>Submitted</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.submission_id}>
                <td>{row.student_id}</td>
                <td>{row.student_name}</td>
                <td>
                  {row.score}/{row.total}
                </td>
                <td>{row.percentage}%</td>
                <td>{row.submitted_at ? new Date(row.submitted_at).toLocaleString() : ""}</td>
                <td>{row.status}</td>
                <td>
                  <Link to={`/results/${row.submission_id}`}>View details</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
