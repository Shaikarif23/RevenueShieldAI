import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatCurrency } from "../../utils/formatCurrency";

export default function RevenueChart({ restaurants }) {
  const data = restaurants.map((item) => ({
    name: item.restaurant_name?.length > 18
      ? `${item.restaurant_name.slice(0, 18)}…`
      : item.restaurant_name,
    Expected: Number(item.expected_revenue || 0),
    Collected: Number(item.collected_revenue || 0),
    Leakage: Number(item.leakage_amount || 0),
  }));

  return (
    <div className="panel chart-panel">
      <div className="panel-heading">
        <div>
          <h3>Restaurant Revenue</h3>
          <span>Expected vs collected vs leakage</span>
        </div>
      </div>
      <div className="chart-wrap">
        {data.length ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis tickFormatter={(v) => `₹${v}`} />
              <Tooltip formatter={(v) => formatCurrency(v)} />
              <Legend />
              <Bar dataKey="Expected" />
              <Bar dataKey="Collected" />
              <Bar dataKey="Leakage" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="chart-empty">No restaurant data</div>
        )}
      </div>
    </div>
  );
}