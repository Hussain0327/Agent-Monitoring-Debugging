"use client";

import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/sidebar";
import { AuthGuard } from "@/components/auth-guard";

const NO_SIDEBAR_PATHS = ["/login"];

export function LayoutShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const showSidebar = !NO_SIDEBAR_PATHS.includes(pathname);

  return (
    <AuthGuard>
      {showSidebar ? (
        <div className="flex h-screen">
          <Sidebar />
          <main className="flex-1 overflow-auto p-6">{children}</main>
        </div>
      ) : (
        <>{children}</>
      )}
    </AuthGuard>
  );
}
