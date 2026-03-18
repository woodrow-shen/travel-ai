"use client";

import { useTranslations } from "next-intl";
import { Card, CardContent } from "@/components/ui/Card";
import type { NotificationLogEntry } from "@/types";

interface NotificationHistoryProps {
  notifications: NotificationLogEntry[];
  isLoading: boolean;
}

export function NotificationHistory({
  notifications,
  isLoading,
}: NotificationHistoryProps) {
  const t = useTranslations("monitor");

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]" />
      </div>
    );
  }

  if (notifications.length === 0) {
    return (
      <p className="text-sm text-[var(--color-muted)]">
        {t("notifications.empty")}
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {notifications.map((n) => (
        <Card key={n.id}>
          <CardContent>
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{n.subject}</p>
                <p className="mt-1 text-sm text-[var(--color-muted)]">
                  {n.email} &middot;{" "}
                  {new Date(n.sent_at).toLocaleString()}
                </p>
              </div>
              <span
                className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${
                  n.status === "sent"
                    ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
                    : "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300"
                }`}
              >
                {t(`notifications.status.${n.status}`)}
              </span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
