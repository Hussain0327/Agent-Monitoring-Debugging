"use client";

import { useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useWebSocket } from "./use-websocket";
import { getToken } from "@/lib/auth";
import type { WebSocketMessage } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

function getWsUrl(): string {
  const token = getToken();
  if (!token) return "";
  const base = API_BASE.replace(/^http/, "ws") || `ws://${typeof window !== "undefined" ? window.location.host : "localhost:8000"}`;
  return `${base}/v1/ws?token=${token}`;
}

export function useLiveUpdates() {
  const queryClient = useQueryClient();
  const url = getWsUrl();

  const onMessage = useCallback(
    (raw: unknown) => {
      const msg = raw as WebSocketMessage;
      if (!msg?.type) return;

      switch (msg.type) {
        case "trace.new":
          queryClient.invalidateQueries({ queryKey: ["traces"] });
          break;
        case "drift.alert":
        case "drift.resolved":
          queryClient.invalidateQueries({ queryKey: ["drift-alerts"] });
          queryClient.invalidateQueries({ queryKey: ["drift-summary"] });
          break;
        case "replay.status":
          queryClient.invalidateQueries({ queryKey: ["replay"] });
          // Also refresh traces if a replay completed (new result trace)
          if ((msg.data as Record<string, unknown>)?.status === "completed") {
            queryClient.invalidateQueries({ queryKey: ["traces"] });
          }
          break;
        case "notification":
          queryClient.invalidateQueries({ queryKey: ["notifications"] });
          queryClient.invalidateQueries({ queryKey: ["notification-count"] });
          break;
      }
    },
    [queryClient],
  );

  const { isConnected, send } = useWebSocket({
    url: url || "ws://unused",
    onMessage,
    reconnectInterval: 5000,
  });

  return { isConnected: url ? isConnected : false, send };
}
