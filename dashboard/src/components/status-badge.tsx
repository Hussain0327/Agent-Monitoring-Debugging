import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

const statusColors: Record<string, string> = {
  ok: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  error: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  unset: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  llm: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  tool: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  chain: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  agent: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400",
  retriever: "bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400",
};

export function StatusBadge({ status, size = "md" }: StatusBadgeProps) {
  const colorClass = statusColors[status] || statusColors.unset;

  return (
    <span
      role="status"
      aria-label={`Status: ${status}`}
      className={cn(
        "inline-flex items-center rounded-full font-medium",
        size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-0.5 text-xs",
        colorClass,
      )}
    >
      {status}
    </span>
  );
}
