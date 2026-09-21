import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { position_to_label_client } from "../labels";

export default function TestDetails() {
  const { testId } = useParams();
  const [test, setTest] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    const data = await api(`/tests/${testId}`);
    setTest(data);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, [testId]);

  async function upload(kind, file) {
    if (!file) return;
    const data = new FormData();
    setError("");
    setMessage("");
    try {
      if (kind === "template") {
        data.append("blank_template", file);
        const result = await api(`/tests/${testId}/template`, { method: "POST", body: data });
        setMessage(result.message);
      } else {
        data.append("answer_key_csv", file);
        await api(`/tests/${testId}/answer-key`, { method: "POST", body: data });
        setMessage("Answer key saved.");
      }
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function setStatus(status) {
    try {
      const updated = await api(`/tests/${testId}`, {
        method: "PUT",
        body: { status },
      });
      setTest(updated);
    } catch (err) {
      setError(err.message);
    }
  }

  if (!test) return <p className="muted">{error || "Loading test…"}</p>;

  return (
    <section className="card">
      <div className="row-between">
        <div>
          <h1>{test.title}</h1>
          <p className="muted">
            Test ID: <strong>{test.test_code}</strong> · {test.question_count} questions ·{" "}
            {test.choice_count} choices · {test.answer_style} · {test.status}
          </p>
        </div>
        <Link className="btn" to={`/teacher/tests/${test.test_code}/results`}>
          View submissions
        </Link>
      </div>
      {error && <p className="error">{error}</p>}
      {message && <p className="ok">{message}</p>}
      <div className="actions">
        {test.status !== "ACTIVE" && (
          <button className="btn primary" type="button" onClick={() => setStatus("ACTIVE")}>
            Activate
          </button>
        )}
        {test.status !== "CLOSED" && (
          <button className="btn" type="button" onClick={() => setStatus("CLOSED")}>
            Close test
          </button>
        )}
      </div>
      <h2>Template</h2>
      <p className="muted">
        {test.layout_json
          ? `Detected ${Object.keys(test.layout_json).length} questions.`
          : "No validated template yet."}
      </p>
      {test.template_path && (
        <img className="preview" src={`/api/tests/${test.test_code}/template-file`} alt="Blank template" />
      )}
      <label>
        Replace template
        <input type="file" accept=".jpg,.jpeg,.png" onChange={(e) => upload("template", e.target.files[0])} />
      </label>
      <h2>Answer key</h2>
      <ul className="key-list">
        {(test.answer_key || []).map((item) => (
          <li key={item.question_number}>
            Q{item.question_number}:{" "}
            {position_to_label_client(item.correct_position, test.answer_style)}
          </li>
        ))}
      </ul>
      <label>
        Replace CSV
        <input type="file" accept=".csv" onChange={(e) => upload("csv", e.target.files[0])} />
      </label>
    </section>
  );
}
