import { useEffect, useState } from "react";
import { getRestaurantLeakage } from "../services/dashboardService";
import { getApiError } from "../services/api";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import EmptyState from "../components/common/EmptyState";
import { formatCurrency } from "../utils/formatCurrency";
import { formatPercentage } from "../utils/formatPercentage";

export default function Restaurants() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setData(await getRestaurantLeakage());
    } catch (err) {
      setError(getApiError(err, "Unable to load restaurant leakage."));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  if (loading) return <Loading text="Loading restaurant analysis..." />;
  if (error) return <ErrorMessage message={error} onRetry={load} />;

  return (
    <div className="page-stack">
      <div className="mini-stats">
        <div><span>Restaurants</span><strong>{data?.total_restaurants || 0}</strong></div>
        <div><span>Highest leakage</span><strong>{formatCurrency(data?.restaurants?.[0]?.leakage_amount || 0)}</strong></div>
      </div>

      {data?.restaurants?.length ? (
        <div className="panel table-panel">
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Restaurant</th>
                  <th>Address</th>
                  <th>Rating</th>
                  <th>Delivered Orders</th>
                  <th>Expected</th>
                  <th>Collected</th>
                  <th>Leakage</th>
                  <th>Leakage %</th>
                </tr>
              </thead>
              <tbody>
                {data.restaurants.map((item) => (
                  <tr key={item.restaurant_id}>
                    <td><strong>{item.restaurant_name}</strong></td>
                    <td>{item.address || "—"}</td>
                    <td>★ {Number(item.rating || 0).toFixed(1)}</td>
                    <td>{item.delivered_orders}</td>
                    <td>{formatCurrency(item.expected_revenue)}</td>
                    <td>{formatCurrency(item.collected_revenue)}</td>
                    <td className={item.leakage_amount ? "danger-text" : "success-text"}>{formatCurrency(item.leakage_amount)}</td>
                    <td>{formatPercentage(item.leakage_percentage)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <EmptyState title="No restaurant data" message="There are no delivered orders for restaurant analysis." />
      )}
    </div>
  );
}