import { useAuth } from "../../context/AuthContext";

export default function Header({ title, subtitle }) {
  const { user, logout } = useAuth();

  return (
    <header className="topbar">
      <div>
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
      <div className="topbar-user">
        <div className="avatar">{(user?.name || "A").charAt(0).toUpperCase()}</div>
        <div className="user-copy">
          <strong>{user?.name || "Admin"}</strong>
          <span>{user?.role || "ADMIN"}</span>
        </div>
        <button className="btn btn-ghost" onClick={logout}>Logout</button>
      </div>
    </header>
  );
}