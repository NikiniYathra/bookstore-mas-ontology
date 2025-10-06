import { useInventoryQuery } from "@/lib/query";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { CheckCircle2, XCircle } from "lucide-react";

export function InventoryTable() {
  const { data, isLoading, isError, error } = useInventoryQuery();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Inventory</CardTitle>
      </CardHeader>
      <CardContent>
        {isError ? (
          <div className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">
            Failed to load inventory: {error.message}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ISBN</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Price</TableHead>
                  <TableHead>Qty</TableHead>
                  <TableHead>Threshold</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading
                  ? Array.from({ length: 5 }).map((_, idx) => (
                      <TableRow key={idx} className="animate-pulse">
                        <TableCell colSpan={6}>
                          <div className="h-4 w-full rounded bg-slate-800" />
                        </TableCell>
                      </TableRow>
                    ))
                  : data?.map((item) => {
                      const low = item.quantity < item.low_threshold || item.needs_restock;
                      return (
                        <TableRow
                          key={item.isbn}
                          className={low ? "bg-red-500/10" : undefined}
                        >
                          <TableCell className="font-mono text-xs">{item.isbn}</TableCell>
                          <TableCell className="max-w-xs truncate">{item.title}</TableCell>
                          <TableCell>${item.price.toFixed(2)}</TableCell>
                          <TableCell>{item.quantity}</TableCell>
                          <TableCell>{item.low_threshold}</TableCell>
                          <TableCell className="flex items-center gap-2">
                            {item.needs_restock ? (
                              <>
                                <XCircle className="h-4 w-4 text-red-400" />
                                <span className="text-red-300 text-xs">Restock</span>
                              </>
                            ) : (
                              <>
                                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                                <span className="text-emerald-300 text-xs">Healthy</span>
                              </>
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
