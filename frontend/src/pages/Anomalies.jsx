import { useEffect, useState } from "react";
import { getAnomalies } from "../services/dashboardService";
import { getApiError } from "../services/api";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import EmptyState from "../components/common/EmptyState";
import { formatCurrency } from "../utils/formatCurrency";
import { riskClass } from "../utils/riskUtils";

export default function Anomalies() {
  const [data, setData] = useState(null);
  const [risk, setRisk] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setData(await getAnomalies({ risk_level: risk }));
    } catch (err) {
      setError(getApiError(err, "Unable to load anomalies."));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [risk]);

  if (loading) return <Loading text="Loading anomalies..." />;
  if (error) return <ErrorMessage message={error} onRetry={load} />;

  return (
    <div className="page-stack">
      <div className="toolbar">
        <div>
          <h2>Detected anomalies</h2>
          <p>{data?.total_anomalies || 0} anomalies found.</p>
        </div>
        <select value={risk} onChange={(e) => setRisk(e.target.value)}>
          <option value="">All risk levels</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>
      </div>

      {data?.anomalies?.length ? (
        <div className="panel table-panel">
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Order</th>
                  <th>Restaurant</th>
                  <th>Type</th>
                  <th>Expected</th>
                  <th>Collected</th>
                  <th>Leakage</th>
                  <th>Risk</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {data.anomalies.map((item) => (
                  <tr key={`${item.anomaly_type}-${item.order_id}`}>
                    <td>#{item.order_id}</td>
                    <td>{item.restaurant_name}</td>
                    <td><span className="type-badge">{item.anomaly_type.replaceAll("_", " ")}</span></td>
                    <td>{formatCurrency(item.expected_revenue)}</td>
                    <td>{formatCurrency(item.collected_revenue)}</td>
                    <td className="danger-text">{formatCurrency(item.leakage_amount)}</td>
                    <td><span className={`badge ${riskClass(item.risk_level)}`}>{item.risk_level} · {item.risk_score}</span></td>
                    <td>{item.risk_reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <EmptyState title="No anomalies" message="No anomalies match the selected risk level." />
      )}
    </div>
  );
}