import { clsx } from "./clsx";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      {...props}
      className={clsx(
        "rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-4 shadow-sm",
        className,
      )}
    />
  );
}

export function Badge({
  color = "zinc",
  className,
  children,
}: {
  color?: "zinc" | "blue" | "orange" | "green" | "red";
  className?: string;
  children: React.ReactNode;
}) {
  const palette: Record<string, string> = {
    zinc: "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
    blue: "bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-300",
    orange: "bg-orange-100 text-orange-800 dark:bg-orange-950 dark:text-orange-300",
    green: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
    red: "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300",
  };
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        palette[color],
        className,
      )}
    >
      {children}
    </span>
  );
}

export function Button({
  variant = "primary",
  className,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "danger";
}) {
  const variants: Record<string, string> = {
    primary:
      "bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-white",
    ghost:
      "bg-transparent text-zinc-700 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800 border border-zinc-200 dark:border-zinc-700",
    danger:
      "bg-rose-600 text-white hover:bg-rose-500 disabled:opacity-60",
  };
  return (
    <button
      {...props}
      className={clsx(
        "inline-flex items-center justify-center rounded-md px-3 py-1.5 text-sm font-medium transition disabled:opacity-60 disabled:cursor-not-allowed",
        variants[variant],
        className,
      )}
    />
  );
}

export function Input({
  className,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={clsx(
        "w-full rounded-md border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:focus:ring-zinc-500",
        className,
      )}
    />
  );
}

export function Textarea({
  className,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      {...props}
      className={clsx(
        "w-full rounded-md border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-3 py-2 text-sm font-mono outline-none focus:ring-2 focus:ring-zinc-400 dark:focus:ring-zinc-500",
        className,
      )}
    />
  );
}

export function Select({
  className,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      className={clsx(
        "rounded-md border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-zinc-400",
        className,
      )}
    />
  );
}

export function platformBadge(platform: string) {
  if (platform === "x")
    return <Badge color="zinc">X</Badge>;
  if (platform === "reddit")
    return <Badge color="orange">Reddit</Badge>;
  return <Badge>{platform}</Badge>;
}

export function statusBadge(status: string) {
  if (status === "ok") return <Badge color="green">ok</Badge>;
  if (status === "reauth_needed")
    return <Badge color="red">re-auth needed</Badge>;
  return <Badge color="red">{status}</Badge>;
}
