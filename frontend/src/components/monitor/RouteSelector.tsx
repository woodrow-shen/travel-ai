"use client";

import { useTranslations } from "next-intl";
import type { Subscription } from "@/types";

interface RouteSelectorProps {
  subscriptions: Subscription[];
  selectedRoute: { origin: string; destination: string } | null;
  onSelect: (route: { origin: string; destination: string } | null) => void;
}

export function RouteSelector({
  subscriptions,
  selectedRoute,
  onSelect,
}: RouteSelectorProps) {
  const t = useTranslations("monitor");

  const routes = Array.from(
    new Map(
      subscriptions
        .filter((s) => s.config.origin && s.config.destination)
        .map((s) => {
          const origin = String(s.config.origin).toUpperCase();
          const destination = String(s.config.destination).toUpperCase();
          return [`${origin}-${destination}`, { origin, destination }];
        })
    ).values()
  );

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    if (!val) {
      onSelect(null);
      return;
    }
    const [origin, destination] = val.split("-");
    onSelect({ origin, destination });
  };

  const currentValue = selectedRoute
    ? `${selectedRoute.origin}-${selectedRoute.destination}`
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
          <option key={`${r.origin}-${r.destination}`} value={`${r.origin}-${r.destination}`}>
            {r.origin} → {r.destination}
          </option>
        ))}
      </select>
    </div>
  );
}
