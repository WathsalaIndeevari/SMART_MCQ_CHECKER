import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { api, downloadUrl } from "../api";

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

  if (error) return <p className="error">{error}</p>;
  if (!result) return <p className="muted">Loading result…</p>;

  return (
    <section className="card">
      <h1>Result</h1>
      <p className="muted">
        {result.student_name} ({result.student_id}) · {result.test_name || result.test_id}
      </p>
      <div className="stats">
        <Stat label="Score" value={`${result.score}/${result.total}`} />
        <Stat label="Percentage" value={`${result.percentage}%`} />
        <Stat label="Correct" value={result.correct_count} />
        <Stat label="Incorrect" value={result.incorrect_count} />
        <Stat label="Unanswered" value={result.unanswered_count} />
        <Stat label="Multiple" value={result.multiple_count} />
      </div>
      <p>
        Status: <strong>{result.status}</strong>
      </p>
      <a className="btn" href={downloadUrl(`/submissions/${result.submission_id}/download`)}>
        Download CSV
      </a>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Q</th>
              <th>Detected</th>
              <th>Correct</th>
              <th>Status</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {(result.questions || []).map((row) => (
              <tr key={row.question_number}>
                <td>{row.question_number}</td>
                <td>{row.detected_label ?? "—"}</td>
                <td>{row.correct_label}</td>
                <td>{row.status}</td>
                <td>{row.confidence ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
