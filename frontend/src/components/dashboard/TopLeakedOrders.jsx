import { formatCurrency } from "../../utils/formatCurrency";
import { riskClass } from "../../utils/riskUtils";

export default function TopLeakedOrders({ orders }) {
  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <h3>Top Leaked Orders</h3>
          <span>Highest revenue leakage</span>
        </div>
      </div>

      {orders.length ? (
        <div className="list">
          {orders.map((item) => (
            <div className="list-row" key={item.order_id}>
              <div className="list-main">
                <strong>Order #{item.order_id}</strong>
                <span>{item.restaurant_name || `Restaurant #${item.restaurant_id}`}</span>
              </div>
              <div className="list-value">
                <strong>{formatCurrency(item.leakage_amount)}</strong>
                <span className={`badge ${riskClass(item.risk_level)}`}>
                  {item.risk_level} · {item.risk_score}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-inline">No leaked orders for the current filters.</div>
      )}
    </div>
  );
}