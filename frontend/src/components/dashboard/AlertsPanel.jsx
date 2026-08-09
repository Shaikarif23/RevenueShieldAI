import { formatCurrency } from "../../utils/formatCurrency";
import { priorityClass } from "../../utils/riskUtils";

export default function AlertsPanel({ alerts = [], loading = false, error = "" }) {
  const safeAlerts = Array.isArray(alerts) ? alerts : [];

  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <h3>Alerts & Recommendations</h3>
          <span>Actions generated from detected anomalies</span>
        </div>
        {safeAlerts.length > 0 && <span>{safeAlerts.length} active</span>}
      </div>

      {loading ? (
        <div className="empty-inline">Loading alerts...</div>
      ) : error ? (
        <div className="filter-error">{error}</div>
      ) : safeAlerts.length ? (
        <div className="alert-list">
          {safeAlerts.slice(0, 4).map((alert, index) => (
            <div
              className={`alert-item ${priorityClass(alert.priority)}`}
              key={`${alert.alert_type || "alert"}-${alert.order_id ?? "na"}-${index}`}
            >
              <div className="alert-top">
                <span className="badge">{alert.priority || "MEDIUM"}</span>
                {Number(alert.leakage_amount) > 0 && (
                  <strong>{formatCurrency(alert.leakage_amount)}</strong>
                )}
              </div>
              <strong>{alert.message || "Revenue risk requires attention."}</strong>
              <span>{alert.recommendation || "Review this anomaly."}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-inline">No active alerts.</div>
      )}
    </div>
  );
}
