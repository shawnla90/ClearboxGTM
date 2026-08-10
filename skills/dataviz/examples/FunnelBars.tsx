"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from "recharts";

const STAGE_COLORS: Record<string, string> = {
  new: "#5b8cff",
  open: "#38d39f",
  trial: "#f59e0b",
  won: "#10b981",
  lost: "#8b93a7",
};

/**
 * Horizontal bar chart for lead/deal funnel stages.
 * Data shape: [{ stage: "new", count: 20 }, { stage: "open", count: 42 }, ...]
 * Source: proof/proof-data.json → leadFunnel or logpose deal pipeline.
 */
export default function FunnelBars({
  data,
}: {
  data: { stage: string; count: number }[];
}) {
  if (!data.length) return <div style={{ color: "#8b93a7", fontSize: 13, padding: 16 }}>No funnel data.</div>;
  return (
    <ResponsiveContainer width="100%" height={Math.max(160, data.length * 40)}>
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 16, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#262b3a" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fill: "#8b93a7", fontSize: 11 }}
          axisLine={{ stroke: "#262b3a" }}
          tickLine={false}
          allowDecimals={false}
        />
        <YAxis
          type="category"
          dataKey="stage"
          tick={{ fill: "#e7ebf3", fontSize: 12 }}
          axisLine={false}
          tickLine={false}
          width={60}
        />
        <Tooltip
          cursor={{ fill: "#1a1e2b" }}
          contentStyle={{
            background: "#131620",
            border: "1px solid #262b3a",
            borderRadius: 8,
            color: "#e7ebf3",
            fontSize: 12,
          }}
        />
        <Bar dataKey="count" name="deals" radius={[0, 4, 4, 0]} maxBarSize={28}>
          {data.map((entry) => (
            <Cell key={entry.stage} fill={STAGE_COLORS[entry.stage] || "#5b8cff"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
