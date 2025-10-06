import { useCustomersQuery, useInventoryQuery, useOrdersQuery, useReportQuery, useRestocksQuery } from "@/lib/query";
import { Controls } from "@/components/Controls";
import { CustomersPanel } from "@/components/CustomersPanel";
import { InventoryTable } from "@/components/InventoryTable";
import { OrdersTable } from "@/components/OrdersTable";
import { InventoryTrend } from "@/components/charts/InventoryTrend";
import { SalesByGenre } from "@/components/charts/SalesByGenre";
import { KpiCard } from "@/components/KpiCard";

export function Dashboard() {
  const { data: inventory } = useInventoryQuery();
  const { data: orders } = useOrdersQuery();
  const { data: customers } = useCustomersQuery();
  const { data: restocks } = useRestocksQuery();
  const { data: report } = useReportQuery();

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard title="Total Sales" value={orders?.length ?? 0} />
        <KpiCard title="Restocks" value={restocks?.length ?? 0} />
        <KpiCard title="Active Customers" value={customers?.length ?? 0} />
        <KpiCard title="Books in Inventory" value={inventory?.length ?? 0} sub={`Reasoner: ${report?.reasoner_active ? "On" : "Fallback"}`} />
      </div>

      <Controls />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <InventoryTable />
        </div>
        <CustomersPanel />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <OrdersTable />
        <SalesByGenre />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <InventoryTrend />
      </div>
    </div>
  );
}
