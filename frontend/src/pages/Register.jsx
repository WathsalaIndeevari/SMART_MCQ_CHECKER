import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");

  async function onSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await register(form.name, form.email, form.password);
      navigate("/teacher");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="card narrow">
      <h1>Create teacher account</h1>
      <form className="form" onSubmit={onSubmit}>
        <label>
          Name
          <input
            required
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </label>
        <label>
          Email
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </label>
        <label>
          Password
          <input
            type="password"
            required
            minLength={6}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn primary" type="submit">
          Register
        </button>
      </form>
      <p className="muted">
        Already registered? <Link to="/teacher/login">Log in</Link>
      </p>
    </section>
  );
}
