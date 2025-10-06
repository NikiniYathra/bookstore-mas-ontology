import { PropsWithChildren } from "react";
import { cn } from "@/lib/utils";

export function Badge({ className, children }: PropsWithChildren<{ className?: string }>) {
  return (
    <span className={cn("inline-flex items-center rounded-full bg-slate-800 px-2 py-0.5 text-xs font-semibold", className)}>
      {children}
    </span>
  );
}
