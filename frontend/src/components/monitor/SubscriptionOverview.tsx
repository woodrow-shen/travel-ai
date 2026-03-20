"use client";

import { useTranslations } from "next-intl";
import { Card, CardContent } from "@/components/ui/Card";
import type { Subscription } from "@/types";
import type { MonitorRoute } from "@/stores/monitor";

interface SubscriptionOverviewProps {
  subscriptions: Subscription[];
  selectedRoute: MonitorRoute | null;
  onSelectRoute: (route: MonitorRoute) => void;
  onToggle: (id: string, isActive: boolean) => void;
}

function formatDate(dateStr: string): string {
  return dateStr.slice(5).replace("-", "/");
}

export function SubscriptionOverview({
  subscriptions,
  selectedRoute,
  onSelectRoute,
  onToggle,
}: SubscriptionOverviewProps) {
  const t = useTranslations("monitor");
  const ts = useTranslations("settings.subscriptions");

  if (subscriptions.length === 0) {
    return (
      <p className="text-sm text-[var(--color-muted)]">
        {t("subscriptions.empty")}
      </p>
    );
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {subscriptions.map((sub) => {
        const origin = String(sub.config.origin ?? "").toUpperCase();
        const destination = String(sub.config.destination ?? "").toUpperCase();
        const depDate = sub.config.departure_date as string | undefined;
        const retDate = sub.config.return_date as string | undefined;

        const isSelected =
          selectedRoute?.origin === origin &&
          selectedRoute?.destination === destination &&
          selectedRoute?.departure_date === depDate &&
          selectedRoute?.return_date === retDate;

        let dateLabel = "";
        if (depDate) {
          dateLabel = formatDate(depDate);
          if (retDate) {
            dateLabel += ` - ${formatDate(retDate)}`;
          }
        }

        return (
          <Card
            key={sub.id}
            className={`cursor-pointer transition-shadow hover:shadow-md ${
              isSelected ? "ring-2 ring-[var(--color-primary)]" : ""
            }`}
            onClick={() =>
              onSelectRoute({
                origin,
                destination,
                departure_date: depDate,
                return_date: retDate,
              })
            }
          >
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">
                    {origin} {retDate ? "↔" : "→"} {destination}
                  </p>
                  {dateLabel && (
                    <p className="text-xs text-[var(--color-muted)]">{dateLabel}</p>
                  )}
                  <span className="mt-1 inline-block rounded-full bg-[var(--color-primary)]/10 px-2 py-0.5 text-xs font-medium text-[var(--color-primary)]">
                    {ts(`types.${sub.type}`)}
                  </span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggle(sub.id, !sub.is_active);
                  }}
                  className={`relative h-6 w-11 rounded-full transition-colors ${
                    sub.is_active
                      ? "bg-[var(--color-primary)]"
                      : "bg-[var(--color-border)]"
                  }`}
                  aria-label={t("subscriptions.toggle")}
                >
                  <span
                    className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
                      sub.is_active ? "left-5" : "left-0.5"
                    }`}
                  />
                </button>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
