import { useOrdersQuery } from "@/lib/query";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from "recharts";

const COLORS = ["#38bdf8", "#c084fc", "#f59e0b", "#34d399", "#f472b6", "#f97316", "#0ea5e9"];

export function SalesByGenre() {
  const { data: orders, isLoading, isError, error } = useOrdersQuery();

  const counts = new Map<string, number>();
  orders?.forEach((order) => {
    const genre = order.genre && order.genre.trim() ? order.genre : "Unknown";
    counts.set(genre, (counts.get(genre) ?? 0) + 1);
  });

  const chartData = Array.from(counts.entries()).map(([name, value]) => ({ name, value }));

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Sales by Genre</CardTitle>
      </CardHeader>
      <CardContent className="h-72">
        {isError ? (
          <div className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">
            Failed to load sales data: {error.message}
          </div>
        ) : isLoading ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-400">
            Loading chart...
          </div>
        ) : chartData.length === 0 ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-400">
            No sales recorded yet.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie dataKey="value" data={chartData} innerRadius={60} outerRadius={100} paddingAngle={4}>
                {chartData.map((_, idx) => (
                  <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: "#0f172a", borderRadius: 12, border: "1px solid #1e293b" }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
