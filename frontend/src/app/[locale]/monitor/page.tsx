"use client";

import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { useMonitor } from "@/hooks/useMonitor";
import { useSubscription } from "@/hooks/useSubscription";
import { RouteSelector } from "@/components/monitor/RouteSelector";
import { PriceTrendChart } from "@/components/monitor/PriceTrendChart";
import { SubscriptionOverview } from "@/components/monitor/SubscriptionOverview";
import { NotificationHistory } from "@/components/monitor/NotificationHistory";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

export default function MonitorPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const t = useTranslations("monitor");
  const tc = useTranslations("common");
  const {
    priceHistory,
    selectedRoute,
    days,
    isLoadingHistory,
    notifications,
    isLoadingNotifications,
    error,
    setSelectedRoute,
    setDays,
  } = useMonitor();
  const { subscriptions, toggleSubscription } = useSubscription();

  if (authLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]" aria-label={tc("loading")} />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <p className="text-center text-[var(--color-muted)]">
          {t("signInRequired")}
        </p>
      </div>
    );
  }

  const dayOptions = [30, 90] as const;

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold">{t("title")}</h1>

      {error && (
        <div
          className="mb-4 rounded-lg bg-[var(--color-error)]/10 px-4 py-3 text-sm text-[var(--color-error)]"
          role="alert"
        >
          {error}
        </div>
      )}

      {/* Route selector + day toggle */}
      <Card className="mb-6">
        <CardContent>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
            <div className="flex-1">
              <RouteSelector
                subscriptions={subscriptions}
                selectedRoute={selectedRoute}
                onSelect={setSelectedRoute}
              />
            </div>
            <div className="flex gap-1 rounded-lg border border-[var(--color-border)] p-0.5">
              {dayOptions.map((d) => (
                <button
                  key={d}
                  onClick={() => setDays(d)}
                  className={cn(
                    "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                    days === d
                      ? "bg-[var(--color-primary)] text-white"
                      : "text-[var(--color-muted)] hover:text-[var(--color-foreground)]"
                  )}
                >
                  {t("chart.days", { count: d })}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Price trend chart */}
      {selectedRoute && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>{t("chart.title")}</CardTitle>
          </CardHeader>
          <CardContent>
            <PriceTrendChart points={priceHistory} isLoading={isLoadingHistory} selectedRoute={selectedRoute} />
          </CardContent>
        </Card>
      )}

      {/* Subscription overview */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>{t("subscriptions.title")}</CardTitle>
        </CardHeader>
        <CardContent>
          <SubscriptionOverview
            subscriptions={subscriptions}
            selectedRoute={selectedRoute}
            onSelectRoute={setSelectedRoute}
            onToggle={toggleSubscription}
          />
        </CardContent>
      </Card>

      {/* Notification history */}
      <Card>
        <CardHeader>
          <CardTitle>{t("notifications.title")}</CardTitle>
        </CardHeader>
        <CardContent>
          <NotificationHistory
            notifications={notifications}
            isLoading={isLoadingNotifications}
          />
        </CardContent>
      </Card>
    </div>
  );
}
