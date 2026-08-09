export default function EmptyState({ title = "No data", message = "Nothing to show." }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">✓</div>
      <strong>{title}</strong>
      <span>{message}</span>
    </div>
  );
}