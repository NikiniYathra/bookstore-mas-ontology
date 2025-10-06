import { z, type ZodTypeAny } from "zod";

const BASE_URL = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

const InventoryItemSchema = z.object({
  isbn: z.string(),
  title: z.string(),
  price: z.number(),
  quantity: z.number(),
  low_threshold: z.number(),
  needs_restock: z.boolean(),
});
const OrderRecordSchema = z.object({
  order_id: z.string(),
  customer: z.string(),
  book: z.string(),
  genre: z.string(),
  step: z.number(),
  price: z.number(),
});
const CustomerSummarySchema = z.object({
  customer_id: z.string(),
  purchased_books: z.array(z.string()),
});
const RestockRecordSchema = z.object({
  step: z.number(),
  isbn: z.string(),
  amount: z.number(),
  employee_id: z.string().nullable().optional(),
});
const RunStepResponseSchema = z.object({
  steps_advanced: z.number(),
  step_count: z.number(),
});
const ResetResponseSchema = z.object({
  step_count: z.number(),
  message: z.string(),
});
const ReportResponseSchema = z.object({
  steps_run: z.number().default(0),
  reasoner_active: z.boolean().default(true),
  inventory: z.array(InventoryItemSchema),
  purchases: z.record(z.array(z.string())),
  restocks: z.array(RestockRecordSchema),
});
const HealthResponseSchema = z.object({
  status: z.string(),
});

export type InventoryItem = z.infer<typeof InventoryItemSchema>;
export type OrderRecord = z.infer<typeof OrderRecordSchema>;
export type CustomerSummary = z.infer<typeof CustomerSummarySchema>;
export type RestockRecord = z.infer<typeof RestockRecordSchema>;
export type RunStepResponse = z.infer<typeof RunStepResponseSchema>;
export type ReportResponse = z.infer<typeof ReportResponseSchema>;
export type ResetResponse = z.infer<typeof ResetResponseSchema>;

async function request<TSchema extends ZodTypeAny>(
  path: string,
  init: RequestInit,
  schema: TSchema
): Promise<z.infer<TSchema>> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(init.headers ?? {}),
    },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed with status ${res.status}`);
  }
  const data = await res.json();
  return schema.parseAsync(data);
}

export async function runStep(payload: {
  steps: number;
  reasoner_sync_interval?: number | null;
  random_seed?: number | null;
}): Promise<RunStepResponse> {
  return request("/run-step", {
    method: "POST",
    body: JSON.stringify(payload),
  }, RunStepResponseSchema);
}

export async function getInventory(): Promise<InventoryItem[]> {
  return request("/inventory", { method: "GET" }, z.array(InventoryItemSchema));
}

export async function getOrders(): Promise<OrderRecord[]> {
  return request("/orders", { method: "GET" }, z.array(OrderRecordSchema));
}

export async function getCustomers(): Promise<CustomerSummary[]> {
  return request("/customers", { method: "GET" }, z.array(CustomerSummarySchema));
}

export async function getRestocks(): Promise<RestockRecord[]> {
  return request("/restocks", { method: "GET" }, z.array(RestockRecordSchema));
}

export async function getReport(): Promise<ReportResponse> {
  return request("/report", { method: "GET" }, ReportResponseSchema);
}

export async function resetSim(): Promise<ResetResponse> {
  return request("/reset", { method: "POST" }, ResetResponseSchema);
}

export async function health(): Promise<{ status: string }> {
  return request("/health", { method: "GET" }, HealthResponseSchema);
}

