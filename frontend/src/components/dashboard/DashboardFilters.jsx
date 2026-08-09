export default function DashboardFilters({ filters, setFilters, restaurants, onApply, onClear }) {
  function update(key, value) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  return (
    <div className="filter-bar">
      <div className="filter-field">
        <label>Restaurant</label>
        <select value={filters.restaurant_id} onChange={(e) => update("restaurant_id", e.target.value)}>
          <option value="">All restaurants</option>
          {restaurants.map((restaurant) => (
            <option key={restaurant.id} value={restaurant.id}>
              {restaurant.restaurant_name}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-field">
        <label>From date</label>
        <input type="date" value={filters.from_date} onChange={(e) => update("from_date", e.target.value)} />
      </div>

      <div className="filter-field">
        <label>To date</label>
        <input type="date" value={filters.to_date} onChange={(e) => update("to_date", e.target.value)} />
      </div>

      <div className="filter-field">
        <label>Risk</label>
        <select value={filters.risk_level} onChange={(e) => update("risk_level", e.target.value)}>
          <option value="">All risk levels</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>
      </div>

      <div className="filter-actions">
        <button className="btn btn-primary" onClick={onApply}>Apply</button>
        <button className="btn btn-secondary" onClick={onClear}>Clear</button>
      </div>
    </div>
  );
}