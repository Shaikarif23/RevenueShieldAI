import { formatCurrency } from "../../utils/formatCurrency";
import { priorityClass } from "../../utils/riskUtils";

export default function AlertsPanel({ alerts }) {
  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <h3>Alerts & Recommendations</h3>
          <span>Actions generated from detected anomalies</span>
        </div>
      </div>

      {alerts.length ? (
        <div className="alert-list">
          {alerts.slice(0, 4).map((alert, index) => (
            <div className={`alert-item ${priorityClass(alert.priority)}`} key={`${alert.order_id}-${index}`}>
              <div className="alert-top">
                <span className="badge">{alert.priority}</span>
                {alert.leakage_amount > 0 && <strong>{formatCurrency(alert.leakage_amount)}</strong>}
              </div>
              <strong>{alert.message}</strong>
              <span>{alert.recommendation}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-inline">No active alerts.</div>
      )}
    </div>
  );
}