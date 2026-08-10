# Dataviz reference architecture

How to turn ClearboxGTM engine output into interactive dashboards.

## The stack

- **Data layer:** SQLite databases (read-only) and engine JSON output
- **Chart library:** [Recharts](https://recharts.org/) 3.x (React, MIT licensed)
- **Framework:** Next.js (App Router, `"use client"` for chart components)
- **Hosting:** Local-first (localhost), deployable to Vercel/Railway

## The pattern

```
engine scripts → JSON/SQLite → API route (read-only) → Recharts component → dashboard page
```

The engine produces the data. The dashboard reads it. They never share a write path. This means:

1. The dashboard never needs database credentials — it reads exported JSON or opens SQLite in `mode=ro`
2. A dashboard crash never corrupts engine state
3. You can run the engine and dashboard on different machines

## Data loading

For a local-first dashboard (the default pattern), load data via a Next.js API route:

```typescript
// app/api/proof/route.ts
import { readFileSync } from "fs";
import { NextResponse } from "next/server";

export async function GET() {
  const data = JSON.parse(
    readFileSync("path/to/proof/proof-data.json", "utf-8")
  );
  return NextResponse.json(data);
}
```

For SQLite, use `better-sqlite3` in read-only mode:

```typescript
import Database from "better-sqlite3";

const db = new Database("path/to/signals.db", { readonly: true });
const rows = db.prepare("SELECT channel, COUNT(*) as n FROM ...").all();
```

## Component anatomy

Every chart component follows the same shape:

```tsx
"use client";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function MyChart({ data }: { data: MyDataShape[] }) {
  if (!data.length) return <div style={{ color: "#8b93a7" }}>No data.</div>;
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#262b3a" vertical={false} />
        <XAxis tick={{ fill: "#8b93a7", fontSize: 11 }} axisLine={{ stroke: "#262b3a" }} tickLine={false} />
        <YAxis tick={{ fill: "#8b93a7", fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={{ background: "#131620", border: "1px solid #262b3a", borderRadius: 8, color: "#e7ebf3" }} />
        <Bar dataKey="value" fill="#5b8cff" radius={[4, 4, 0, 0]} maxBarSize={44} />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

Key conventions:

- `ResponsiveContainer` wraps every chart (never hardcoded widths)
- `CartesianGrid` uses the grid color (`#262b3a`), vertical lines off
- Tooltip background matches the card (`#131620`)
- Empty-state guard at the top of every component

## The palette

| Token | Hex | CSS variable |
|---|---|---|
| `--bg` | `#131620` | Tooltip/card background |
| `--grid` | `#262b3a` | Grid lines, borders |
| `--blue` | `#5b8cff` | Primary series |
| `--green` | `#38d39f` | Positive / success |
| `--red` | `#ef4444` | Negative / alert |
| `--amber` | `#f59e0b` | Warning / neutral |
| `--muted` | `#8b93a7` | Labels, secondary text |
| `--text` | `#e7ebf3` | Primary text |

Define these as CSS custom properties in your layout:

```css
:root {
  --bg: #131620;
  --grid: #262b3a;
  --blue: #5b8cff;
  --green: #38d39f;
  --red: #ef4444;
  --amber: #f59e0b;
  --muted: #8b93a7;
  --text: #e7ebf3;
}
```

## What to chart first

If you are starting from scratch, these three charts cover the essential GTM dashboard:

1. **Channel attribution bars** (`ChannelBars.tsx`) — where signups come from, first-touch
2. **Engagement over time** (`ImpressionsLine.tsx`) — whether the motion is growing
3. **Lead funnel** (`FunnelBars.tsx`) — conversion stages at a glance

From there, add competitor share-of-voice (donut chart, compose from the ChannelBars pattern) and sentiment distribution (stacked bar, same pattern).

## Bootstrapping a dashboard project

```bash
npx create-next-app@latest my-gtm-dashboard --typescript --tailwind --app
cd my-gtm-dashboard
npm install recharts better-sqlite3
# copy examples/ into components/
cp path/to/ClearboxGTM/skills/dataviz/examples/*.tsx components/
```

The example components are self-contained — no shared imports, no project-specific dependencies.
