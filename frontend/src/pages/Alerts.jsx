import { useEffect, useState } from "react";
import { getAlerts } from "../services/dashboardService";
import { getApiError } from "../services/api";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import EmptyState from "../components/common/EmptyState";
import { formatCurrency } from "../utils/formatCurrency";
import { priorityClass } from "../utils/riskUtils";

export default function Alerts() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setData(await getAlerts());
    } catch (err) {
      setError(getApiError(err, "Unable to load alerts."));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  if (loading) return <Loading text="Loading alerts..." />;
  if (error) return <ErrorMessage message={error} onRetry={load} />;

  return (
    <div className="page-stack">
      <div className="mini-stats">
        <div><span>Critical</span><strong>{data?.critical_alerts || 0}</strong></div>
        <div><span>High</span><strong>{data?.high_alerts || 0}</strong></div>
        <div><span>Medium</span><strong>{data?.medium_alerts || 0}</strong></div>
        <div><span>Total</span><strong>{data?.total_alerts || 0}</strong></div>
      </div>

      {data?.alerts?.length ? (
        <div className="alert-page-list">
          {data.alerts.map((alert, index) => (
            <div className={`big-alert ${priorityClass(alert.priority)}`} key={`${alert.order_id}-${index}`}>
              <div className="big-alert-header">
                <span className="badge">{alert.priority}</span>
                <span>{alert.alert_type.replaceAll("_", " ")}</span>
                {alert.leakage_amount > 0 && <strong>{formatCurrency(alert.leakage_amount)}</strong>}
              </div>
              <h3>{alert.message}</h3>
              <p>{alert.recommendation}</p>
              <small>{alert.restaurant_name} · Order #{alert.order_id}</small>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState title="No active alerts" message="RevenueShield has no alerts to review." />
      )}
    </div>
  );
}