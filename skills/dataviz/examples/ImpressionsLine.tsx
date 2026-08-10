"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

/**
 * Time-series line chart for engagement or impressions over time.
 * Data shape: [{ date: "2026-07-01", impressions: 12400 }, ...]
 * Source: engine output aggregated by day, or proof/proof-data.json era history.
 */
export default function ImpressionsLine({
  data,
}: {
  data: { date: string; impressions: number }[];
}) {
  if (!data.length) return <div style={{ color: "#8b93a7", fontSize: 13, padding: 16 }}>No metrics yet.</div>;
  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#262b3a" vertical={false} />
        <XAxis
          dataKey="date"
          tick={{ fill: "#8b93a7", fontSize: 10 }}
          axisLine={{ stroke: "#262b3a" }}
          tickLine={false}
          minTickGap={30}
        />
        <YAxis
          tick={{ fill: "#8b93a7", fontSize: 10 }}
          axisLine={false}
          tickLine={false}
          width={60}
          tickFormatter={(v: number) => (v >= 1000 ? `${Math.round(v / 1000)}k` : String(v))}
        />
        <Tooltip
          contentStyle={{
            background: "#131620",
            border: "1px solid #262b3a",
            borderRadius: 8,
            color: "#e7ebf3",
            fontSize: 12,
          }}
        />
        <Line type="monotone" dataKey="impressions" stroke="#38d39f" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
