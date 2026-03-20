"use client";

import { useTranslations } from "next-intl";
import type { Subscription } from "@/types";
import type { MonitorRoute } from "@/stores/monitor";

interface RouteSelectorProps {
  subscriptions: Subscription[];
  selectedRoute: MonitorRoute | null;
  onSelect: (route: MonitorRoute | null) => void;
}

interface RouteOption extends MonitorRoute {
  label: string;
  value: string;
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return `${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")}`;
}

export function RouteSelector({
  subscriptions,
  selectedRoute,
  onSelect,
}: RouteSelectorProps) {
  const t = useTranslations("monitor");

  const routes: RouteOption[] = Array.from(
    new Map(
      subscriptions
        .filter((s) => s.config.origin && s.config.destination)
        .map((s) => {
          const origin = String(s.config.origin).toUpperCase();
          const destination = String(s.config.destination).toUpperCase();
          const departure_date = s.config.departure_date as string | undefined;
          const return_date = s.config.return_date as string | undefined;
          const tripType = s.config.trip_type as string | undefined;

          const value = `${origin}-${destination}-${departure_date ?? ""}-${return_date ?? ""}`;

          let dateInfo = "";
          if (departure_date) {
            dateInfo = ` | ${formatDate(departure_date)}`;
            if (return_date) {
              dateInfo += ` - ${formatDate(return_date)} (${t("routeSelector.roundtrip")})`;
            } else {
              dateInfo += ` (${t("routeSelector.oneway")})`;
            }
          }

          const label = `${origin} → ${destination}${dateInfo}`;

          return [
            value,
            { origin, destination, departure_date, return_date, label, value },
          ] as [string, RouteOption];
        })
    ).values()
  );

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    if (!val) {
      onSelect(null);
      return;
    }
    const route = routes.find((r) => r.value === val);
    if (route) {
      onSelect({
        origin: route.origin,
        destination: route.destination,
        departure_date: route.departure_date,
        return_date: route.return_date,
      });
    }
  };

  const currentValue = selectedRoute
    ? `${selectedRoute.origin}-${selectedRoute.destination}-${selectedRoute.departure_date ?? ""}-${selectedRoute.return_date ?? ""}`
    : "";

  return (
    <div>
      <label
        htmlFor="route-selector"
        className="mb-1 block text-sm font-medium text-[var(--color-muted)]"
      >
        {t("routeSelector.label")}
      </label>
      <select
        id="route-selector"
        value={currentValue}
        onChange={handleChange}
        className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-sm text-[var(--color-foreground)]"
      >
        <option value="">{t("routeSelector.placeholder")}</option>
        {routes.map((r) => (
          <option key={r.value} value={r.value}>
            {r.label}
          </option>
        ))}
      </select>
    </div>
  );
}
