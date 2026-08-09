import { formatCurrency } from "../../utils/formatCurrency";
import { riskClass } from "../../utils/riskUtils";

export default function RecentAnomalies({ anomalies }) {
  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <h3>Recent Anomalies</h3>
          <span>Latest detected issues</span>
        </div>
      </div>

      <div className="list">
        {anomalies.map((item) => (
          <div className="list-row" key={`${item.anomaly_type}-${item.order_id}`}>
            <div className="list-main">
              <strong>Order #{item.order_id}</strong>
              <span>{item.anomaly_type.replaceAll("_", " ")}</span>
              <small>{item.risk_reason}</small>
            </div>
            <div className="list-value">
              <strong>{formatCurrency(item.leakage_amount)}</strong>
              <span className={`badge ${riskClass(item.risk_level)}`}>{item.risk_level}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}