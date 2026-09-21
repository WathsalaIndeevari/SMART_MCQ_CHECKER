import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="shell">
      <header className="topbar">
        <Link to="/" className="brand">
          SnapScore
        </Link>
        <nav>
          <NavLink to="/submit">Submit sheet</NavLink>
          {user ? (
            <>
              <NavLink to="/teacher">Dashboard</NavLink>
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
