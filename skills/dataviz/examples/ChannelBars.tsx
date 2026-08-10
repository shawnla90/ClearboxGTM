"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

/**
 * Vertical bar chart for channel attribution (first-touch or last-touch signups).
 * Data shape: [{ channel: "referral", n: 54 }, { channel: "web", n: 51 }, ...]
 * Source: proof/proof-data.json → logpose.signups_by_channel
 */
export default function ChannelBars({
  data,
  color = "#5b8cff",
}: {
  data: { channel: string; n: number }[];
  color?: string;
}) {
  if (!data.length) return <div style={{ color: "#8b93a7", fontSize: 13, padding: 16 }}>No data yet.</div>;
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#262b3a" vertical={false} />
        <XAxis
          dataKey="channel"
          tick={{ fill: "#8b93a7", fontSize: 11 }}
          axisLine={{ stroke: "#262b3a" }}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "#8b93a7", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          allowDecimals={false}
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
        <Bar dataKey="n" name="signups" fill={color} radius={[4, 4, 0, 0]} maxBarSize={44} />
      </BarChart>
    </ResponsiveContainer>
  );
}
