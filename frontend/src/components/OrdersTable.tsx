import { useMemo, useState } from "react";
import { useOrdersQuery } from "@/lib/query";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";

export function OrdersTable() {
  const { data, isLoading, isError, error } = useOrdersQuery();
  const [customerFilter, setCustomerFilter] = useState("");
  const [isbnFilter, setIsbnFilter] = useState("");

  const filtered = useMemo(() => {
    if (!data) return [];
    return data.filter((order) => {
      const matchesCustomer =
        !customerFilter ||
        order.customer.toLowerCase().includes(customerFilter.toLowerCase());
      const matchesIsbn =
        !isbnFilter || order.book.toLowerCase().includes(isbnFilter.toLowerCase());
      return matchesCustomer && matchesIsbn;
    });
  }, [data, customerFilter, isbnFilter]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Orders</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid gap-3 md:grid-cols-2">
          <Input
            placeholder="Filter by customer…"
            value={customerFilter}
            onChange={(e) => setCustomerFilter(e.target.value)}
          />
          <Input
            placeholder="Filter by ISBN…"
            value={isbnFilter}
            onChange={(e) => setIsbnFilter(e.target.value)}
          />
        </div>
        {isError ? (
          <div className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">
            Failed to load orders: {error.message}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Order</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Book</TableHead>
                  <TableHead>Step</TableHead>
                  <TableHead>Price</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading
                  ? Array.from({ length: 5 }).map((_, idx) => (
                      <TableRow key={idx} className="animate-pulse">
                        <TableCell colSpan={5}>
                          <div className="h-4 w-full rounded bg-slate-800" />
                        </TableCell>
                      </TableRow>
                    ))
                  : filtered.map((order) => (
                      <TableRow key={order.order_id}>
                        <TableCell className="font-mono text-xs">{order.order_id}</TableCell>
                        <TableCell>{order.customer}</TableCell>
                        <TableCell className="font-mono text-xs">{order.book}</TableCell>
                        <TableCell>{order.step}</TableCell>
                        <TableCell>${order.price.toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                {!isLoading && filtered.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="py-6 text-center text-sm text-slate-400">
                      No orders match the current filters.
                    </TableCell>
                  </TableRow>
                ) : null}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
