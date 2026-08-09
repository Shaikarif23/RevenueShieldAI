import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import Header from "./Header";

const pageMeta = {
  "/dashboard": ["Revenue Dashboard", "Real-time revenue leakage monitoring"],
  "/alerts": ["Alerts & Recommendations", "Prioritized actions for detected revenue risks"],
  "/anomalies": ["Anomalies", "Detected revenue and data-quality issues"],
  "/restaurants": ["Restaurants", "Restaurant-level revenue leakage analysis"],
};

export default function DashboardLayout() {
  const location = useLocation();
  const [title, subtitle] = pageMeta[location.pathname] || ["RevenueShield AI", "Admin control center"];

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <Header title={title} subtitle={subtitle} />
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}