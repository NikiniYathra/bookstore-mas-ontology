import { cn } from "@/lib/utils";
import { PropsWithChildren, TableHTMLAttributes, forwardRef } from "react";

export const Table = forwardRef<HTMLTableElement, TableHTMLAttributes<HTMLTableElement>>(
  ({ className, ...props }, ref) => (
    <table
      ref={ref}
      className={cn("w-full caption-bottom text-sm text-left text-slate-200", className)}
      {...props}
    />
  )
);

Table.displayName = "Table";

export function TableHeader({ className, children }: PropsWithChildren<{ className?: string }>) {
  return <thead className={cn("[&_tr]:border-b border-slate-800", className)}>{children}</thead>;
}

export function TableBody({ className, children }: PropsWithChildren<{ className?: string }>) {
  return <tbody className={cn("divide-y divide-slate-800", className)}>{children}</tbody>;
}

export function TableRow({ className, children }: PropsWithChildren<{ className?: string }>) {
  return <tr className={cn("transition-colors hover:bg-slate-800", className)}>{children}</tr>;
}

export function TableHead({ className, children }: PropsWithChildren<{ className?: string }>) {
  return (
    <th
      scope="col"
      className={cn("px-3 py-2 text-xs font-semibold uppercase tracking-wide text-slate-400", className)}
    >
      {children}
    </th>
  );
}

export function TableCell({ className, children }: PropsWithChildren<{ className?: string }>) {
  return <td className={cn("px-3 py-2 align-middle", className)}>{children}</td>;
}
