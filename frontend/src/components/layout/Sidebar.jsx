import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const links = [
  { to: "/dashboard", label: "Dashboard", icon: "▦" },
  { to: "/alerts", label: "Alerts", icon: "!" },
  { to: "/anomalies", label: "Anomalies", icon: "△" },
  { to: "/restaurants", label: "Restaurants", icon: "⌂" },
];

export default function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">RS</div>
        <div>
          <strong>RevenueShield</strong>
          <small>AI Control Center</small>
        </div>
      </div>

      <nav className="nav-list">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <span className="nav-icon">{link.icon}</span>
            <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span className="status-dot" />
        <div>
          <strong>{user?.name || "Admin"}</strong>
          <small>{user?.email || "ADMIN"}</small>
        </div>
      </div>
    </aside>
  );
}