import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(email, password);
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
          <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>⚡</div>
          <h1>Teacher login</h1>
          <p className="muted">Sign in to manage your tests and view results.</p>
        </div>

        <form id="login-form" className="form" onSubmit={onSubmit}>
          <label>
            Email address
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@school.edu"
            />
          </label>
          <label>
            Password
            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </label>

          {error && <p className="alert alert-error">{error}</p>}

          <button id="login-btn" className="btn primary lg" type="submit" disabled={busy}>
            {busy ? <><span className="spinner" /> Signing in…</> : "Sign in →"}
          </button>
        </form>

        <p className="muted" style={{ textAlign: "center", marginTop: "1.25rem", fontSize: "0.875rem" }}>
          New teacher?{" "}
          <Link to="/teacher/register">Create an account</Link>
        </p>
      </div>
    </section>
  );
}
