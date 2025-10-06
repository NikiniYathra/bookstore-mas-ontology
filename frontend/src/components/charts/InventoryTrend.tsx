import { useReportQuery } from "@/lib/query";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

export function InventoryTrend() {
  const { data, isLoading, isError, error } = useReportQuery();

  const chartData =
    data?.inventory.map((item) => ({
      name: item.title,
      quantity: item.quantity,
      threshold: item.low_threshold,
    })) ?? [];

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Inventory vs. Threshold</CardTitle>
      </CardHeader>
      <CardContent className="h-72">
        {isError ? (
          <div className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">
            Failed to load inventory trend: {error.message}
          </div>
        ) : isLoading ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-400">
            Loading chart…
          </div>
        ) : chartData.length === 0 ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-400">
            No inventory data available.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip
                contentStyle={{ backgroundColor: "#0f172a", borderRadius: 12, border: "1px solid #1e293b" }}
              />
              <Legend />
              <Line type="monotone" dataKey="quantity" stroke="#38bdf8" strokeWidth={2} dot />
              <Line type="monotone" dataKey="threshold" stroke="#f97316" strokeWidth={2} dot />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
