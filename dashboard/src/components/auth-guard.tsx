"use client";

/**
 * AuthGuard is now a pass-through — the app is fully browsable without login.
 * Auth is only needed for write operations (replay, settings, etc.)
 * which the API layer handles with 401 responses.
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
