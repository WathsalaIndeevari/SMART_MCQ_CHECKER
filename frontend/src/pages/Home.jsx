import { Link } from "react-router-dom";

export default function Home() {
  return (
    <section className="hero-card">
      <p className="eyebrow">Web-based OMR grading</p>
      <h1>Score MCQ sheets from a phone photo.</h1>
      <p className="lead">
        Teachers upload a blank bubble sheet and a CSV answer key. Students upload a
        scanned or photographed answer sheet and get a score with per-question feedback.
      </p>
      <div className="actions">
        <Link className="btn primary" to="/submit">
          Submit an answer sheet
        </Link>
        <Link className="btn" to="/teacher/login">
          Teacher login
        </Link>
      </div>
    </section>
  );
}
