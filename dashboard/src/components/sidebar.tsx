"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, AlertTriangle, LayoutDashboard, List, Settings, LogOut, LogIn } from "lucide-react";
import { cn } from "@/lib/utils";
import { isAuthenticated, logout } from "@/lib/auth";
import { NotificationBell } from "@/components/notification-bell";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/traces", label: "Traces", icon: List },
  { href: "/drift", label: "Drift", icon: AlertTriangle },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const authed = isAuthenticated();

  return (
    <aside
      role="navigation"
      aria-label="Main navigation"
      className="flex h-full w-[var(--sidebar-width)] flex-col border-r border-[var(--border)] bg-[var(--background-raised)]"
    >
      {/* Logo */}
      <div className="flex items-center justify-between border-b border-[var(--border)] px-5 py-4">
        <Link href="/" className="group flex items-center gap-2.5">
          <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--accent-dim)] transition-all group-hover:glow-accent-sm">
            <Activity size={18} className="text-[var(--accent)]" />
            <div className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-[var(--accent)] animate-pulse-dot" />
          </div>
          <div>
            <span className="text-base font-semibold tracking-tight">Vigil</span>
            <span className="ml-1.5 font-mono text-[10px] text-[var(--muted-foreground)]">v0.1</span>
          </div>
        </Link>
        {authed && <NotificationBell />}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-3">
        <div className="mb-2 px-3 font-mono text-[10px] font-medium uppercase tracking-widest text-[var(--muted-foreground)]">
          Navigate
        </div>
        <div className="space-y-0.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href ||
              (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-150",
                  isActive
                    ? "bg-[var(--accent-dim)] text-[var(--accent-text)]"
                    : "text-[var(--muted-foreground)] hover:bg-[var(--background-elevated)] hover:text-[var(--foreground)]",
                )}
              >
                {isActive && (
                  <div className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-[var(--accent)]" />
                )}
                <Icon size={16} className={cn(
                  "transition-colors",
                  isActive ? "text-[var(--accent)]" : "text-[var(--muted-foreground)] group-hover:text-[var(--foreground)]"
                )} />
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="border-t border-[var(--border)] px-3 py-3">
        {authed ? (
          <button
            onClick={logout}
            className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-[var(--muted-foreground)] transition-colors hover:bg-[var(--danger-dim)] hover:text-[var(--danger)]"
          >
            <LogOut size={14} />
            Sign out
          </button>
        ) : (
          <Link
            href="/login"
            className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-[var(--muted-foreground)] transition-colors hover:bg-[var(--accent-dim)] hover:text-[var(--accent-text)]"
          >
            <LogIn size={14} />
            Sign in
          </Link>
        )}
      </div>
    </aside>
  );
}
