import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

export default function CreateTest() {
  const navigate = useNavigate();
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

  async function onSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");
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
      setMessage(
        created.template_status?.message ||
          `Saved ${created.test_code} as ${created.status}.`,
      );
      navigate(`/teacher/tests/${created.test_code}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card">
      <h1>Create test</h1>
      <form className="form" onSubmit={onSubmit}>
        <label>
          Test title
          <input
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
        </label>
        <div className="grid-2">
          <label>
            Number of questions
            <input
              type="number"
              min="1"
              required
              value={form.question_count}
              onChange={(e) => setForm({ ...form, question_count: e.target.value })}
            />
          </label>
          <label>
            Choices per question
            <input
              type="number"
              min="2"
              max="5"
              required
              value={form.choice_count}
              onChange={(e) => setForm({ ...form, choice_count: e.target.value })}
            />
          </label>
        </div>
        <label>
          Answer style
          <select
            value={form.answer_style}
            onChange={(e) => setForm({ ...form, answer_style: e.target.value })}
          >
            <option value="ALPHABETIC">Alphabetic (A–E)</option>
            <option value="NUMERIC">Numeric (1–5)</option>
          </select>
        </label>
        <label>
          Blank OMR template
          <input type="file" accept=".jpg,.jpeg,.png" onChange={(e) => setTemplate(e.target.files[0])} />
        </label>
        <label>
          Answer-key CSV
          <input type="file" accept=".csv" onChange={(e) => setCsv(e.target.files[0])} />
        </label>
        {error && <p className="error">{error}</p>}
        {message && <p className="ok">{message}</p>}
        <button className="btn primary" type="submit" disabled={busy}>
          {busy ? "Processing…" : "Save test"}
        </button>
      </form>
    </section>
  );
}
