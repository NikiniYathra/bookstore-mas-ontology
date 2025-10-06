import {
    QueryClient,
    QueryClientProvider,
    useQuery,
    useMutation,
    useQueryClient,
  } from "@tanstack/react-query";
  import { PropsWithChildren } from "react";
  import * as api from "./api";
  
  export const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 10,
        refetchOnWindowFocus: false,
        retry: 1,
      },
    },
  });
  
  export function QueryProvider({ children }: PropsWithChildren) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }
  
  export const queryKeys = {
    inventory: ["inventory"] as const,
    orders: ["orders"] as const,
    customers: ["customers"] as const,
    restocks: ["restocks"] as const,
    report: ["report"] as const,
    health: ["health"] as const,
  };
  
  export function useInventoryQuery() {
    return useQuery({
      queryKey: queryKeys.inventory,
      queryFn: api.getInventory,
    });
  }
  
  export function useOrdersQuery() {
    return useQuery({
      queryKey: queryKeys.orders,
      queryFn: api.getOrders,
    });
  }
  
  export function useCustomersQuery() {
    return useQuery({
      queryKey: queryKeys.customers,
      queryFn: api.getCustomers,
    });
  }
  
  export function useRestocksQuery() {
    return useQuery({
      queryKey: queryKeys.restocks,
      queryFn: api.getRestocks,
    });
  }
  
  export function useReportQuery() {
    return useQuery({
      queryKey: queryKeys.report,
      queryFn: api.getReport,
    });
  }
  
  export function useRunStepMutation() {
    const client = useQueryClient();
    return useMutation({
      mutationFn: api.runStep,
      onSettled: () => {
        client.invalidateQueries({ queryKey: queryKeys.inventory });
        client.invalidateQueries({ queryKey: queryKeys.orders });
        client.invalidateQueries({ queryKey: queryKeys.customers });
        client.invalidateQueries({ queryKey: queryKeys.restocks });
        client.invalidateQueries({ queryKey: queryKeys.report });
      },
    });
  }
  
  export function useResetMutation() {
    const client = useQueryClient();
    return useMutation({
      mutationFn: api.resetSim,
      onSettled: () => {
        client.invalidateQueries({ queryKey: queryKeys.inventory });
        client.invalidateQueries({ queryKey: queryKeys.orders });
        client.invalidateQueries({ queryKey: queryKeys.customers });
        client.invalidateQueries({ queryKey: queryKeys.restocks });
        client.invalidateQueries({ queryKey: queryKeys.report });
      },
    });
  }
  