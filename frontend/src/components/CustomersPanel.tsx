import { Users } from "lucide-react";
import { useCustomersQuery } from "@/lib/query";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";

export function CustomersPanel() {
  const { data, isLoading, isError, error } = useCustomersQuery();

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Customers</CardTitle>
        <Badge className="bg-slate-800 text-slate-200">
          <Users className="mr-1 h-3 w-3" />
          {data?.length ?? 0}
        </Badge>
      </CardHeader>
      <CardContent className="space-y-3">
        {isError ? (
          <div className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">
            Failed to load customers: {error.message}
          </div>
        ) : isLoading ? (
          Array.from({ length: 4 }).map((_, idx) => (
            <div key={idx} className="h-10 animate-pulse rounded-lg bg-slate-800" />
          ))
        ) : (
          data?.map((customer) => (
            <div key={customer.customer_id} className="rounded-lg border border-slate-800 bg-slate-900 p-3">
              <div className="flex items-center justify-between">
                <span className="font-medium">{customer.customer_id}</span>
                <Badge>{customer.purchased_books.length} books</Badge>
              </div>
              <p className="mt-2 text-xs text-slate-400">
                {customer.purchased_books.length > 0
                  ? customer.purchased_books.join(", ")
                  : "No purchases"}
              </p>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
