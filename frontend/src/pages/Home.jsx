import { Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

const features = [
  { icon: "📷", title: "Phone camera works", desc: "Snap a clear photo — no scanner needed." },
  { icon: "⚡", title: "Instant results", desc: "Scores and per-question feedback in seconds." },
  { icon: "🎯", title: "Smart detection", desc: "Handles multi-mark, blank, and ambiguous bubbles." },
  { icon: "📊", title: "CSV export", desc: "Download results for your gradebook in one click." },
  { icon: "🔒", title: "No student accounts", desc: "Students submit with their ID — no sign-up." },
  { icon: "🗂️", title: "Any format", desc: "A–E or 1–5 labelling, 2–5 choices, any question count." },
];

export default function Home() {
  const { user } = useAuth();

  return (
    <section>
      <div className="hero">
        <p className="eyebrow">⚡ Web-based OMR grading</p>
        <h1>Grade MCQ sheets from<br />a phone photo.</h1>
        <p className="lead">
          Teachers upload a blank bubble sheet and a CSV answer key.
          Students photograph their completed sheet and receive an instant score
          with per-question feedback — no installation, no scanner.
        </p>
        <div className="actions">
          <Link className="btn primary lg" to="/submit">
            📋 Submit an answer sheet
          </Link>
          {user ? (
            <Link className="btn lg" to="/teacher">
              Dashboard →
            </Link>
          ) : (
            <Link className="btn lg" to="/teacher/login">
              Teacher login
            </Link>
          )}
        </div>

        <div className="feature-grid">
          {features.map((f) => (
            <div className="feature-item" key={f.title}>
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
