import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useTrip } from "../useTrip";
import { useTripStore } from "@/stores/trip";

vi.mock("@/lib/api", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

import { api } from "@/lib/api";

const mockTrip = {
  id: "trip-1",
  title: "Tokyo Trip",
  description: "Spring vacation",
  destination: "Tokyo",
  start_date: "2026-04-01",
  end_date: "2026-04-07",
  created_at: "2026-03-01T00:00:00Z",
  updated_at: "2026-03-01T00:00:00Z",
};

describe("useTrip", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useTripStore.setState({
      trips: [],
      selectedTrip: null,
      isLoading: false,
      error: null,
    });
  });

  it("starts with empty state", () => {
    const { result } = renderHook(() => useTrip());
    expect(result.current.trips).toEqual([]);
    expect(result.current.selectedTrip).toBeNull();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("fetchTrips loads trips", async () => {
    vi.mocked(api.get).mockResolvedValueOnce([mockTrip]);

    const { result } = renderHook(() => useTrip());

    await act(async () => {
      await result.current.fetchTrips();
    });

    expect(api.get).toHaveBeenCalledWith("/trips");
    expect(result.current.trips).toEqual([mockTrip]);
  });

  it("fetchTrips handles error", async () => {
    vi.mocked(api.get).mockRejectedValueOnce({ detail: "Unauthorized" });

    const { result } = renderHook(() => useTrip());

    await act(async () => {
      await result.current.fetchTrips();
    });

    expect(result.current.error).toBe("Unauthorized");
  });

  it("fetchTrip selects a single trip", async () => {
    vi.mocked(api.get).mockResolvedValueOnce(mockTrip);

    const { result } = renderHook(() => useTrip());

    await act(async () => {
      const trip = await result.current.fetchTrip("trip-1");
      expect(trip).toEqual(mockTrip);
    });

    expect(result.current.selectedTrip).toEqual(mockTrip);
  });

  it("createTrip adds trip to store", async () => {
    vi.mocked(api.post).mockResolvedValueOnce(mockTrip);

    const { result } = renderHook(() => useTrip());

    await act(async () => {
      const trip = await result.current.createTrip({
        title: "Tokyo Trip",
        destination: "Tokyo",
        start_date: "2026-04-01",
        end_date: "2026-04-07",
      });
      expect(trip).toEqual(mockTrip);
    });

    expect(result.current.trips).toContainEqual(mockTrip);
  });

  it("updateTrip updates trip in store", async () => {
    useTripStore.setState({ trips: [mockTrip] });
    const updated = { ...mockTrip, title: "Updated Trip" };
    vi.mocked(api.patch).mockResolvedValueOnce(updated);

    const { result } = renderHook(() => useTrip());

    await act(async () => {
      await result.current.updateTrip("trip-1", { title: "Updated Trip" });
    });

    expect(result.current.trips[0].title).toBe("Updated Trip");
  });

  it("deleteTrip removes trip from store", async () => {
    useTripStore.setState({ trips: [mockTrip] });
    vi.mocked(api.delete).mockResolvedValueOnce(undefined);

    const { result } = renderHook(() => useTrip());

    await act(async () => {
      const success = await result.current.deleteTrip("trip-1");
      expect(success).toBe(true);
    });

    expect(result.current.trips).toEqual([]);
  });

  it("deleteTrip handles error", async () => {
    useTripStore.setState({ trips: [mockTrip] });
    vi.mocked(api.delete).mockRejectedValueOnce(new Error("fail"));

    const { result } = renderHook(() => useTrip());

    await act(async () => {
      const success = await result.current.deleteTrip("trip-1");
      expect(success).toBe(false);
    });

    expect(result.current.error).toBe("Failed to delete trip.");
    expect(result.current.trips).toContainEqual(mockTrip);
  });
});
