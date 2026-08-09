import { riskClass } from "../../utils/riskUtils";

export default function RiskCard({ level, count }) {
  return (
    <div className={`risk-card ${riskClass(level)}`}>
      <span>{level}</span>
      <strong>{count}</strong>
      <small>anomalies</small>
    </div>
  );
}