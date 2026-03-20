import { describe, it, expect, beforeEach, vi } from "vitest";
import { useMonitorStore } from "../monitor";
import { api } from "@/lib/api";
import type { PriceHistoryResponse, NotificationLogEntry } from "@/types";

vi.mock("@/lib/api", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockPriceHistoryResponse: PriceHistoryResponse = {
  origin: "TPE",
  destination: "NRT",
  departure_date: null,
  return_date: null,
  days: 30,
  points: [
    {
      id: "ph-1",
      origin: "TPE",
      destination: "NRT",
      departure_date: "2026-04-01",
      return_date: null,
      price_amount: 8500,
      price_currency: "TWD",
      source: "amadeus",
      airline: "BR",
      cabin_class: "economy",
      stops: 0,
      created_at: "2026-03-01T00:00:00Z",
    },
    {
      id: "ph-2",
      origin: "TPE",
      destination: "NRT",
      departure_date: "2026-04-01",
      return_date: null,
      price_amount: 9200,
      price_currency: "TWD",
      source: "skyscanner",
      airline: null,
      cabin_class: null,
      stops: null,
      created_at: "2026-03-02T00:00:00Z",
    },
  ],
};

const mockNotifications: NotificationLogEntry[] = [
  {
    id: "n-1",
    subscription_id: "sub-1",
    email: "test@example.com",
    subject: "Bug Fare: TPE → NRT",
    sent_at: "2026-03-15T10:00:00Z",
    status: "sent",
  },
  {
    id: "n-2",
    subscription_id: "sub-1",
    email: "test@example.com",
    subject: "Price Drop: TPE → NRT",
    sent_at: "2026-03-14T08:00:00Z",
    status: "failed",
  },
];

describe("useMonitorStore", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useMonitorStore.setState({
      priceHistory: [],
      selectedRoute: null,
      days: 30,
      isLoadingHistory: false,
      notifications: [],
      isLoadingNotifications: false,
      error: null,
    });
  });

  it("starts with default state", () => {
    const state = useMonitorStore.getState();
    expect(state.priceHistory).toEqual([]);
    expect(state.selectedRoute).toBeNull();
    expect(state.days).toBe(30);
    expect(state.isLoadingHistory).toBe(false);
    expect(state.notifications).toEqual([]);
    expect(state.isLoadingNotifications).toBe(false);
    expect(state.error).toBeNull();
  });

  describe("fetchPriceHistory", () => {
    it("sets price history on success", async () => {
      vi.mocked(api.get).mockResolvedValue(mockPriceHistoryResponse);
      await useMonitorStore.getState().fetchPriceHistory("TPE", "NRT");
      const state = useMonitorStore.getState();
      expect(state.priceHistory).toEqual(mockPriceHistoryResponse.points);
      expect(state.isLoadingHistory).toBe(false);
      expect(state.error).toBeNull();
      expect(api.get).toHaveBeenCalledWith("/price-history", {
        origin: "TPE",
        destination: "NRT",
        days: "30",
      });
    });

    it("uses custom days parameter", async () => {
      vi.mocked(api.get).mockResolvedValue({ ...mockPriceHistoryResponse, days: 90 });
      await useMonitorStore.getState().fetchPriceHistory("TPE", "NRT", 90);
      expect(api.get).toHaveBeenCalledWith("/price-history", {
        origin: "TPE",
        destination: "NRT",
        days: "90",
      });
    });

    it("sets error on failure", async () => {
      vi.mocked(api.get).mockRejectedValue({ detail: "Unauthorized" });
      await useMonitorStore.getState().fetchPriceHistory("TPE", "NRT");
      const state = useMonitorStore.getState();
      expect(state.error).toBe("Unauthorized");
      expect(state.isLoadingHistory).toBe(false);
      expect(state.priceHistory).toEqual([]);
    });

    it("uses fallback error message", async () => {
      vi.mocked(api.get).mockRejectedValue(new Error("network"));
      await useMonitorStore.getState().fetchPriceHistory("TPE", "NRT");
      expect(useMonitorStore.getState().error).toBe("Failed to fetch price history");
    });
  });

  describe("fetchNotifications", () => {
    it("sets notifications on success", async () => {
      vi.mocked(api.get).mockResolvedValue(mockNotifications);
      await useMonitorStore.getState().fetchNotifications();
      const state = useMonitorStore.getState();
      expect(state.notifications).toEqual(mockNotifications);
      expect(state.isLoadingNotifications).toBe(false);
      expect(state.error).toBeNull();
      expect(api.get).toHaveBeenCalledWith("/subscriptions/notifications");
    });

    it("sets error on failure", async () => {
      vi.mocked(api.get).mockRejectedValue({ detail: "Server error" });
      await useMonitorStore.getState().fetchNotifications();
      const state = useMonitorStore.getState();
      expect(state.error).toBe("Server error");
      expect(state.isLoadingNotifications).toBe(false);
    });

    it("uses fallback error message", async () => {
      vi.mocked(api.get).mockRejectedValue(new Error("fail"));
      await useMonitorStore.getState().fetchNotifications();
      expect(useMonitorStore.getState().error).toBe("Failed to fetch notifications");
    });
  });

  describe("setSelectedRoute", () => {
    it("sets route", () => {
      useMonitorStore.getState().setSelectedRoute({ origin: "TPE", destination: "NRT" });
      expect(useMonitorStore.getState().selectedRoute).toEqual({
        origin: "TPE",
        destination: "NRT",
      });
    });

    it("clears route with null", () => {
      useMonitorStore.setState({ selectedRoute: { origin: "TPE", destination: "NRT" } });
      useMonitorStore.getState().setSelectedRoute(null);
      expect(useMonitorStore.getState().selectedRoute).toBeNull();
    });
  });

  describe("setDays", () => {
    it("updates days value", () => {
      useMonitorStore.getState().setDays(90);
      expect(useMonitorStore.getState().days).toBe(90);
    });
  });
});
