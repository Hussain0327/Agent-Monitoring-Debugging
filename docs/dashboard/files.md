# Dashboard Source Files

Every file in `dashboard/src/` explained in plain language.

## `app/layout.tsx` — The Page Frame
The root layout that wraps every page. Sets up the HTML structure, applies global styles, and renders the sidebar + main content area. All pages appear inside this frame.

## `app/providers.tsx` — The Data Plumbing
Configures React Query's `QueryClient` with a 5-second stale time and wraps the app in the provider. This enables all components to use `useQuery` for data fetching with automatic caching.

## `app/page.tsx` — The Home Dashboard
The landing page showing two panels: a latency metrics chart at the top and a trace list table below. This is what you see when you open the dashboard.

## `app/drift/page.tsx` — The Drift Monitor
Displays drift detection results. Shows summary stats (total alerts, unresolved, high severity) at the top, then lists individual drift alerts as cards with severity colors and trend indicators.

## `app/traces/[id]/page.tsx` — The Trace Explorer
A dynamic route that shows a single trace in detail. The left panel has a collapsible span tree; clicking a span shows its full details (input, output, events, metadata) in the right panel.

## `components/sidebar.tsx` — The Navigation Bar
The left sidebar with the Vigil logo, navigation links (Dashboard, Drift), and a version footer. Highlights the current page using Next.js pathname detection.

## `components/trace-list.tsx` — The Trace Table
Renders a table of all traces with columns for name, status, span count, duration, and timestamp. Each trace name links to its detail page. Shows loading/error/empty states.

## `components/metrics-chart.tsx` — The Latency Graph
An area chart showing latency trends over time using Recharts. Fetches real span data from the API and computes hourly latency buckets. Falls back to a placeholder when no data is available.

## `components/span-tree.tsx` — The Span Explorer
A recursive tree component where each span can be expanded/collapsed to show children. Displays status badge, span name, kind label, and duration. Clicking selects a span for detail viewing.

## `components/span-detail.tsx` — The Span Inspector
Shows everything about a selected span: name, kind, status, duration, timing, and ID. Renders input and output as formatted JSON in code blocks. Lists events with timestamps.

## `components/status-badge.tsx` — The Status Pill
A small colored badge indicating status (ok=green, error=red, unset=gray) or span kind (llm=purple, tool=blue, chain=amber). Comes in small and medium sizes.

## `components/drift-alert-card.tsx` — The Alert Card
Displays a single drift alert with severity-colored border (yellow/orange/red), the metric name, PSI score, percentage change, baseline-to-current values, and a "Resolved" badge when applicable.

## `hooks/use-traces.ts` — The Trace Fetcher
React Query hooks for trace data. `useTraces()` fetches the paginated trace list with 5-second auto-refresh. `useTrace(id)` fetches a single trace with its spans.

## `hooks/use-websocket.ts` — The Live Wire
A WebSocket hook for real-time data streaming. Handles connection, reconnection (every 3 seconds), JSON parsing, and cleanup. Stores the `onMessage` callback in a ref to avoid reconnection loops.

## `lib/types.ts` — The Type Dictionary
TypeScript interfaces for all data structures: Span, Trace, TraceListResponse, DriftAlert, DriftSummary, SpanTreeNode, and union types for SpanKind and SpanStatus.

## `lib/api.ts` — The HTTP Client
Wrapper around `fetch` for API calls. Provides `api.traces.list()`, `api.traces.get()`, `api.spans.list()`, `api.drift.alerts()`, and `api.drift.summary()`. Handles errors with a custom `APIError` class.

## `lib/utils.ts` — The Utility Belt
Helper functions: `cn()` merges Tailwind classes, `formatDuration()` converts timestamps to human-readable durations, `formatDate()` formats ISO dates, `buildSpanTree()` converts a flat span list into a parent-child tree.
