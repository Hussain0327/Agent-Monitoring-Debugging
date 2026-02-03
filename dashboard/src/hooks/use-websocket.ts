"use client";

import { useEffect, useRef, useState, useCallback } from "react";

interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: unknown) => void;
  reconnectInterval?: number;
}

export function useWebSocket({ url, onMessage, reconnectInterval = 3000 }: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>(undefined);
  const onMessageRef = useRef(onMessage);

  // Keep the callback ref current without triggering reconnects
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const connect = useCallback(() => {
    // Clear any pending reconnect timer before creating a new connection
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = undefined;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessageRef.current?.(data);
      } catch {
        // Ignore non-JSON messages
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      reconnectTimer.current = setTimeout(connect, reconnectInterval);
    };

    ws.onerror = () => {
      ws.close();
    };

    wsRef.current = ws;
  }, [url, reconnectInterval]);

  useEffect(() => {
    connect();
    return () => {
      // Clear pending reconnect timer on cleanup
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = undefined;
      }
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return { isConnected, send };
}
