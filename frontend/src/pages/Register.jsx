import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function field(key) {
    return (e) => setForm({ ...form, [key]: e.target.value });
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await register(form.name, form.email, form.password);
      navigate("/teacher");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section style={{ display: "flex", justifyContent: "center" }}>
      <div className="card" style={{ width: "100%", maxWidth: 440 }}>
        <div style={{ textAlign: "center", marginBottom: "1.75rem" }}>
          <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>🎓</div>
          <h1>Create teacher account</h1>
          <p className="muted">Join SnapScore to create and manage graded tests.</p>
        </div>

        <form id="register-form" className="form" onSubmit={onSubmit}>
          <label>
            Full name
            <input
              id="name"
              required
              autoComplete="name"
              value={form.name}
              onChange={field("name")}
              placeholder="Dr. Jane Smith"
            />
          </label>
          <label>
            Email address
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={form.email}
              onChange={field("email")}
              placeholder="you@school.edu"
            />
          </label>
          <label>
            Password
            <input
              id="password"
              type="password"
              required
              minLength={6}
              autoComplete="new-password"
              value={form.password}
              onChange={field("password")}
              placeholder="At least 6 characters"
            />
          </label>

          {error && <p className="alert alert-error">{error}</p>}

          <button id="register-btn" className="btn primary lg" type="submit" disabled={busy}>
            {busy ? <><span className="spinner" /> Creating account…</> : "Create account →"}
          </button>
        </form>

        <p className="muted" style={{ textAlign: "center", marginTop: "1.25rem", fontSize: "0.875rem" }}>
          Already registered?{" "}
          <Link to="/teacher/login">Sign in</Link>
        </p>
      </div>
    </section>
  );
}
