import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate("/teacher");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="card narrow">
      <h1>Teacher login</h1>
      <form className="form" onSubmit={onSubmit}>
        <label>
          Email
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label>
          Password
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn primary" type="submit">
          Log in
        </button>
      </form>
      <p className="muted">
        New teacher? <Link to="/teacher/register">Create an account</Link>
      </p>
    </section>
  );
}
