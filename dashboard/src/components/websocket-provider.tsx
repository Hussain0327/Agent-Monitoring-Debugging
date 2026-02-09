"use client";

import { type ReactNode } from "react";
import { useLiveUpdates } from "@/hooks/use-live-updates";

export function WebSocketProvider({ children }: { children: ReactNode }) {
  // Just initialize the WebSocket connection — invalidation happens automatically
  useLiveUpdates();
  return <>{children}</>;
}
