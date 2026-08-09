export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="error-box">
      <strong>Unable to load data</strong>
      <span>{message}</span>
      {onRetry && <button className="btn btn-secondary" onClick={onRetry}>Retry</button>}
    </div>
  );
}