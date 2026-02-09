import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

const statusConfig: Record<string, { bg: string; text: string; dot: string }> = {
  ok: { bg: "bg-[var(--success-dim)]", text: "text-[var(--success)]", dot: "bg-[var(--success)]" },
  error: { bg: "bg-[var(--danger-dim)]", text: "text-[var(--danger)]", dot: "bg-[var(--danger)]" },
  unset: { bg: "bg-[var(--background-elevated)]", text: "text-[var(--muted-foreground)]", dot: "bg-[var(--muted-foreground)]" },
  llm: { bg: "bg-purple-500/10", text: "text-purple-400", dot: "bg-purple-400" },
  tool: { bg: "bg-blue-500/10", text: "text-blue-400", dot: "bg-blue-400" },
  chain: { bg: "bg-amber-500/10", text: "text-amber-400", dot: "bg-amber-400" },
  agent: { bg: "bg-[var(--accent-dim)]", text: "text-[var(--accent)]", dot: "bg-[var(--accent)]" },
  retriever: { bg: "bg-teal-500/10", text: "text-teal-400", dot: "bg-teal-400" },
  custom: { bg: "bg-[var(--background-elevated)]", text: "text-[var(--muted-foreground)]", dot: "bg-[var(--muted-foreground)]" },
};

export function StatusBadge({ status, size = "md" }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.unset;

  return (
    <span
      role="status"
      aria-label={`Status: ${status}`}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md font-mono font-medium",
        size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-0.5 text-[11px]",
        config.bg,
        config.text,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", config.dot)} />
      {status}
    </span>
  );
}
