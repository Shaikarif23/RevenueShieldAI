import { formatCurrency } from "../../utils/formatCurrency";
import { formatPercentage } from "../../utils/formatPercentage";

export default function RestaurantLeakageTable({ restaurants }) {
  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <h3>Restaurant Leakage</h3>
          <span>Highest leakage first</span>
        </div>
      </div>

      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Restaurant</th>
              <th>Orders</th>
              <th>Expected</th>
              <th>Collected</th>
              <th>Leakage</th>
              <th>Leakage %</th>
            </tr>
          </thead>
          <tbody>
            {restaurants.map((item) => (
              <tr key={item.restaurant_id}>
                <td>
                  <strong>{item.restaurant_name}</strong>
                  <small>{item.address || "—"}</small>
                </td>
                <td>{item.delivered_orders}</td>
                <td>{formatCurrency(item.expected_revenue)}</td>
                <td>{formatCurrency(item.collected_revenue)}</td>
                <td className={item.leakage_amount > 0 ? "danger-text" : "success-text"}>
                  {formatCurrency(item.leakage_amount)}
                </td>
                <td>{formatPercentage(item.leakage_percentage)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}