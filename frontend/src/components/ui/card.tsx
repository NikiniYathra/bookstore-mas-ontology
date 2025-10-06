import { cn } from "@/lib/utils";
import { PropsWithChildren } from "react";

export function Card({ className, children }: PropsWithChildren<{ className?: string }>) {
  return (
    <div className={cn("rounded-2xl border border-slate-800 bg-slate-900 shadow-sm", className)}>
      {children}
    </div>
  );
}

export function CardHeader({ className, children }: PropsWithChildren<{ className?: string }>) {
  return <div className={cn("p-4 pb-0", className)}>{children}</div>;
}

export function CardTitle({ className, children }: PropsWithChildren<{ className?: string }>) {
  return <h3 className={cn("text-lg font-semibold", className)}>{children}</h3>;
}

export function CardContent({ className, children }: PropsWithChildren<{ className?: string }>) {
  return <div className={cn("p-4 pt-2", className)}>{children}</div>;
}

export function CardFooter({ className, children }: PropsWithChildren<{ className?: string }>) {
  return <div className={cn("p-4 pt-0", className)}>{children}</div>;
}
