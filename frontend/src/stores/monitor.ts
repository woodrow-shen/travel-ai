import { create } from "zustand";
import { api } from "@/lib/api";
import type {
  NotificationLogEntry,
  PriceHistoryPoint,
  PriceHistoryResponse,
} from "@/types";

interface MonitorState {
  priceHistory: PriceHistoryPoint[];
  selectedRoute: { origin: string; destination: string } | null;
  days: number;
  isLoadingHistory: boolean;
  notifications: NotificationLogEntry[];
  isLoadingNotifications: boolean;
  error: string | null;

  fetchPriceHistory: (
    origin: string,
    destination: string,
    days?: number
  ) => Promise<void>;
  fetchNotifications: () => Promise<void>;
  setSelectedRoute: (route: { origin: string; destination: string } | null) => void;
  setDays: (days: number) => void;
}

export const useMonitorStore = create<MonitorState>((set, get) => ({
  priceHistory: [],
  selectedRoute: null,
  days: 30,
  isLoadingHistory: false,
  notifications: [],
  isLoadingNotifications: false,
  error: null,

  fetchPriceHistory: async (origin, destination, days) => {
    const d = days ?? get().days;
    set({ isLoadingHistory: true, error: null });
    try {
      const data = await api.get<PriceHistoryResponse>("/price-history", {
        origin,
        destination,
        days: String(d),
      });
      set({ priceHistory: data.points, isLoadingHistory: false });
    } catch (err: unknown) {
      const message =
        (err as { detail?: string }).detail ?? "Failed to fetch price history";
      set({ error: message, isLoadingHistory: false });
    }
  },

  fetchNotifications: async () => {
    set({ isLoadingNotifications: true, error: null });
    try {
      const data = await api.get<NotificationLogEntry[]>(
        "/subscriptions/notifications"
      );
      set({ notifications: data, isLoadingNotifications: false });
    } catch (err: unknown) {
      const message =
        (err as { detail?: string }).detail ?? "Failed to fetch notifications";
      set({ error: message, isLoadingNotifications: false });
    }
  },

  setSelectedRoute: (route) => set({ selectedRoute: route }),

  setDays: (days) => set({ days }),
}));
