"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, AlertTriangle, LayoutDashboard } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/drift", label: "Drift", icon: AlertTriangle },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      role="navigation"
      aria-label="Main navigation"
      className="flex h-full w-[var(--sidebar-width)] flex-col border-r border-[var(--border)] bg-[var(--muted)]"
    >
      <div className="flex items-center gap-2 border-b border-[var(--border)] px-4 py-4">
        <Activity size={24} className="text-vigil-600" />
        <span className="text-lg font-bold">Vigil</span>
      </div>

      <nav className="flex-1 p-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive ? "page" : undefined}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-vigil-100 text-vigil-700 dark:bg-vigil-900/30 dark:text-vigil-300"
                  : "text-[var(--muted-foreground)] hover:bg-[var(--border)] hover:text-[var(--foreground)]",
              )}
            >
              <Icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-[var(--border)] px-4 py-3 text-xs text-[var(--muted-foreground)]">
        Vigil v0.1.0
      </div>
    </aside>
  );
}
