import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const isTeacherArea = location.pathname.startsWith("/teacher");

  const initials = user?.name
    ? user.name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase()
    : "T";

  return (
    <div className="shell">
      <header className="topbar">
        <Link to="/" className="brand">
          <span className="brand-icon">⚡</span>
          SnapScore
        </Link>

        <nav>
          <NavLink to="/submit">Submit sheet</NavLink>
          {user ? (
            <>
              <NavLink to="/teacher">Dashboard</NavLink>
              <div className="user-badge">
                <div className="user-avatar">{initials}</div>
                {user.name?.split(" ")[0]}
              </div>
              <button type="button" className="linkish" onClick={logout}>
                Log out
              </button>
            </>
          ) : (
            <NavLink to="/teacher/login">Teacher login</NavLink>
          )}
        </nav>
      </header>

      <main className="page">
        <Outlet />
      </main>
    </div>
  );
}
