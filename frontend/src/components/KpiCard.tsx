import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface KpiCardProps {
  title: string;
  value: string | number;
  sub?: string;
}

export function KpiCard({ title, value, sub }: KpiCardProps) {
  return (
    <Card className="bg-gradient-to-br from-slate-900 to-slate-950">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-slate-400">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-semibold">{value}</div>
        {sub ? <p className="mt-1 text-sm text-slate-400">{sub}</p> : null}
      </CardContent>
    </Card>
  );
}
