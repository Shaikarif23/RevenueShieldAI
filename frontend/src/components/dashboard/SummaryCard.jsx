export default function SummaryCard({ label, value, hint, tone = "" }) {
  return (
    <div className={`summary-card ${tone}`}>
      <span className="summary-label">{label}</span>
      <strong className="summary-value">{value}</strong>
      {hint && <span className="summary-hint">{hint}</span>}
    </div>
  );
}