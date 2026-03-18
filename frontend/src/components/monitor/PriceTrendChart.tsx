"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { PriceHistoryPoint } from "@/types";

const SOURCE_COLORS: Record<string, string> = {
  amadeus: "#2563eb",
  skyscanner: "#059669",
  kiwi: "#d97706",
  google_flights: "#dc2626",
};

interface PriceTrendChartProps {
  points: PriceHistoryPoint[];
  isLoading: boolean;
}

export function PriceTrendChart({ points, isLoading }: PriceTrendChartProps) {
  const t = useTranslations("monitor");

  const { chartData, sources } = useMemo(() => {
    if (points.length === 0) return { chartData: [], sources: [] };

    const sourceSet = new Set<string>();
    const byDate = new Map<string, Record<string, number>>();

    for (const pt of points) {
      const dateKey = new Date(pt.created_at).toLocaleDateString();
      sourceSet.add(pt.source);

      if (!byDate.has(dateKey)) {
        byDate.set(dateKey, { date: dateKey } as unknown as Record<string, number>);
      }
      const entry = byDate.get(dateKey)!;
      // Keep the latest price per source per date
      (entry as Record<string, unknown>)[pt.source] = pt.price_amount;
      (entry as Record<string, unknown>)["date"] = dateKey;
    }

    return {
      chartData: Array.from(byDate.values()),
      sources: Array.from(sourceSet),
    };
  }, [points]);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]" />
      </div>
    );
  }

  if (chartData.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-[var(--color-muted)]">
        {t("chart.noData")}
      </div>
    );
  }

  const currency = points[0]?.price_currency ?? "";

  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12, fill: "var(--color-muted)" }}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "var(--color-muted)" }}
            tickFormatter={(v: number) => `${currency} ${v.toLocaleString()}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--color-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "8px",
            }}
            formatter={(value) => [
              `${currency} ${Number(value).toLocaleString()}`,
            ]}
          />
          <Legend />
          {sources.map((source) => (
            <Line
              key={source}
              type="monotone"
              dataKey={source}
              stroke={SOURCE_COLORS[source] ?? "#6b7280"}
              strokeWidth={2}
              dot={{ r: 3 }}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
