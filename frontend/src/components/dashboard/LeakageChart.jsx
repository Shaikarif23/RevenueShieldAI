import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { formatCurrency } from "../../utils/formatCurrency";

export default function LeakageChart({ summary }) {
  const data = [
    { name: "Collected", value: Number(summary?.delivered_collected_revenue || 0) },
    { name: "Leakage", value: Number(summary?.total_leakage || 0) },
  ].filter((item) => item.value > 0);

  return (
    <div className="panel chart-panel small-chart">
      <div className="panel-heading">
        <div>
          <h3>Delivered Revenue</h3>
          <span>Collected vs leakage</span>
        </div>
      </div>
      <div className="chart-wrap">
        {data.length ? (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} dataKey="value" nameKey="name" innerRadius={60} outerRadius={95} paddingAngle={3}>
                {data.map((entry, index) => <Cell key={entry.name} />)}
              </Pie>
              <Tooltip formatter={(v) => formatCurrency(v)} />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="chart-empty">No delivered revenue</div>
        )}
      </div>
    </div>
  );
}