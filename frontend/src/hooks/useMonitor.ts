"use client";

import { useEffect } from "react";
import { useMonitorStore } from "@/stores/monitor";

export function useMonitor() {
  const priceHistory = useMonitorStore((s) => s.priceHistory);
  const selectedRoute = useMonitorStore((s) => s.selectedRoute);
  const days = useMonitorStore((s) => s.days);
  const isLoadingHistory = useMonitorStore((s) => s.isLoadingHistory);
  const notifications = useMonitorStore((s) => s.notifications);
  const isLoadingNotifications = useMonitorStore((s) => s.isLoadingNotifications);
  const error = useMonitorStore((s) => s.error);
  const fetchPriceHistory = useMonitorStore((s) => s.fetchPriceHistory);
  const fetchNotifications = useMonitorStore((s) => s.fetchNotifications);
  const setSelectedRoute = useMonitorStore((s) => s.setSelectedRoute);
  const setDays = useMonitorStore((s) => s.setDays);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  useEffect(() => {
    if (selectedRoute) {
      fetchPriceHistory(
        selectedRoute.origin,
        selectedRoute.destination,
        days,
        selectedRoute.departure_date,
        selectedRoute.return_date,
      );
    }
  }, [selectedRoute, days, fetchPriceHistory]);

  return {
    priceHistory,
    selectedRoute,
    days,
    isLoadingHistory,
    notifications,
    isLoadingNotifications,
    error,
    setSelectedRoute,
    setDays,
  };
}
