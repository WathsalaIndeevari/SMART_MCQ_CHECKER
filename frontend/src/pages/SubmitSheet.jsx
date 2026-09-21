import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

export default function SubmitSheet() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    test_id: "",
    student_id: "",
    student_name: "",
  });
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function onFile(event) {
    const next = event.target.files?.[0];
    setFile(next || null);
    setPreview(next ? URL.createObjectURL(next) : "");
  }

  async function onSubmit(event) {
    event.preventDefault();
    setError("");
    if (!file) {
      setError("Please upload a JPG or PNG of the completed sheet.");
      return;
    }
    const data = new FormData();
    data.append("student_id", form.student_id);
    data.append("student_name", form.student_name);
    data.append("sheet", file);
    setBusy(true);
    try {
      const result = await api(`/tests/${encodeURIComponent(form.test_id)}/submissions`, {
        method: "POST",
        body: data,
      });
      navigate(`/results/${result.submission_id}`, { state: result });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card">
      <h1>Submit answer sheet</h1>
      <p className="muted">
        Use a well-lit photo of the full page. Avoid heavy shadows, cropped edges, and blur.
      </p>
      <form className="form" onSubmit={onSubmit}>
        <label>
          Test ID
          <input
            required
            value={form.test_id}
            onChange={(e) => setForm({ ...form, test_id: e.target.value })}
            placeholder="TEST-A3K9"
          />
        </label>
        <label>
          Student ID
          <input
            required
            value={form.student_id}
            onChange={(e) => setForm({ ...form, student_id: e.target.value })}
            placeholder="ST001"
          />
        </label>
        <label>
          Student name
          <input
            required
            value={form.student_name}
            onChange={(e) => setForm({ ...form, student_name: e.target.value })}
          />
        </label>
        <label>
          Answer sheet (JPG, JPEG, PNG)
          <input required type="file" accept=".jpg,.jpeg,.png" onChange={onFile} />
        </label>
        {preview && <img className="preview" src={preview} alt="Answer sheet preview" />}
        {error && <p className="error">{error}</p>}
        <button className="btn primary" type="submit" disabled={busy}>
          {busy ? "Evaluating…" : "Submit for evaluation"}
        </button>
      </form>
    </section>
  );
}
