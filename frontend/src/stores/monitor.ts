import { create } from "zustand";
import { api } from "@/lib/api";
import type {
  NotificationLogEntry,
  PriceHistoryPoint,
  PriceHistoryResponse,
} from "@/types";

export interface MonitorRoute {
  origin: string;
  destination: string;
  departure_date?: string;
  return_date?: string;
}

interface MonitorState {
  priceHistory: PriceHistoryPoint[];
  selectedRoute: MonitorRoute | null;
  days: number;
  isLoadingHistory: boolean;
  notifications: NotificationLogEntry[];
  isLoadingNotifications: boolean;
  error: string | null;

  fetchPriceHistory: (
    origin: string,
    destination: string,
    days?: number,
    departure_date?: string,
    return_date?: string
  ) => Promise<void>;
  fetchNotifications: () => Promise<void>;
  setSelectedRoute: (route: MonitorRoute | null) => void;
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

  fetchPriceHistory: async (origin, destination, days, departure_date, return_date) => {
    const d = days ?? get().days;
    set({ isLoadingHistory: true, error: null });
    try {
      const params: Record<string, string> = {
        origin,
        destination,
        days: String(d),
      };
      if (departure_date) params.departure_date = departure_date;
      if (return_date) params.return_date = return_date;

      const data = await api.get<PriceHistoryResponse>("/price-history", params);
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
