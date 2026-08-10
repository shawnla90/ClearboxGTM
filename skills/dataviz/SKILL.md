---
name: dataviz
version: 1.0.0
description: Reference architecture for GTM dashboards with Recharts — the palette, the component patterns, and the data contract from SQLite to chart. Use when the user says "/dataviz", "build a dashboard", "visualize these signals", or "show me a chart".
---

# dataviz

The reference architecture for turning engine output into visual dashboards.

This skill documents the Recharts component patterns, the dark-theme palette, and the data contract that connects the ClearboxGTM engine's SQLite output to interactive charts. The `examples/` directory contains standalone `.tsx` components you can copy into a Next.js project.

## The data contract

Every chart reads from the engine's JSON or SQLite output — never from a separate data source:

| Engine output | Chart type | Example component |
|---|---|---|
| `proof/proof-data.json` → signup attribution | Bar chart | `examples/ChannelBars.tsx` |
| `data/signals.db` → thread engagement over time | Line chart | `examples/ImpressionsLine.tsx` |
| `proof/proof-data.json` → lead funnel stages | Horizontal bar | `examples/FunnelBars.tsx` |
| `data/competitor_analysis.json` → share of voice | Donut / bar | (compose from ChannelBars pattern) |
| `data/last24.json` → fresh signal feed | Table + sparkline | (compose from ImpressionsLine pattern) |

## The palette

Consistent across all chart components — a dark theme that reads well on both dashboards and embedded views:

| Token | Hex | Use |
|---|---|---|
| `bg` | `#131620` | Tooltip and card backgrounds |
| `grid` | `#262b3a` | Grid lines, borders |
| `blue` | `#5b8cff` | Primary data series |
| `green` | `#38d39f` | Positive / success series |
| `red` | `#ef4444` | Negative / alert series |
| `amber` | `#f59e0b` | Warning / neutral series |
| `muted` | `#8b93a7` | Tick labels, secondary text |
| `text` | `#e7ebf3` | Primary text |

## How to use the examples

The `examples/` directory contains standalone React components. They are reference code — not runnable within the ClearboxGTM repo (this is a Python-first repo with no `package.json` at root).

To use them:

1. Copy the `.tsx` file into a Next.js or React project with `recharts` installed
2. Pass your engine JSON as the `data` prop
3. Adjust the `dataKey` props to match your output shape

```bash
# in your Next.js project
npm install recharts
# then import the component
```

## Rules

1. **Charts read engine output, not raw databases.** The engine scripts produce the JSON; the charts render it. This separation means the chart layer never needs database credentials.
2. **The palette is shared.** Use the tokens above for visual consistency across dashboards.
3. **Label generated data.** If a chart shows sentiment or other LLM-generated values, include a note in the chart caption or tooltip.

## Related

- `../../engine/` — the scripts that produce the data these charts render
- `../../proof/` — the generated proof data (the first data source most dashboards will use)
- `../competitor-intel/` — produces competitor_analysis.json, a natural chart source
- `../../playbooks/attribution-tracking.md` — the journey materialization pattern the ChannelBars component visualizes
