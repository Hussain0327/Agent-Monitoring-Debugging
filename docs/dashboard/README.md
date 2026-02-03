# Vigil Dashboard

The Vigil Dashboard is a Next.js 15 web application for visualizing traces, exploring spans, and monitoring drift in your AI agent pipelines.

## Running

```bash
cd dashboard
npm install
npm run dev
# Dashboard runs at http://localhost:3000
```

## Features

- **Trace List** — Browse all traces with status, span count, duration, and timestamps
- **Trace Detail** — Explore spans in a collapsible tree view with input/output inspection
- **Drift Monitoring** — View drift alerts with severity, PSI scores, and trend indicators
- **Metrics Chart** — Latency visualization over time
- **Real-time Updates** — Auto-refresh every 5 seconds via React Query

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| Next.js | 15.1 | React framework with App Router |
| React | 19.0 | UI library |
| React Query | 5.62 | Data fetching and caching |
| Recharts | 2.15 | Charts and visualizations |
| Tailwind CSS | 3.4 | Utility-first styling |
| Lucide React | 0.468 | Icon library |

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `""` | Vigil server URL |

## Project Structure

```
src/
├── app/           # Next.js App Router pages
├── components/    # Reusable React components
├── hooks/         # Custom React hooks
└── lib/           # Types, API client, utilities
```

See [Dashboard Files](files.md) for details on every source file.
