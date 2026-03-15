import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useCompare } from "../useCompare";

vi.mock("@/lib/api", () => ({
  api: {
    post: vi.fn(),
  },
}));

import { api } from "@/lib/api";

const mockResults = [
  {
    item_id: "flight-1",
    item_type: "flight" as const,
    label: "CI100 TPE → NRT (direct)",
    prices: [
      { provider: "amadeus", price: 15000, currency: "TWD", fetched_at: "2026-03-15T00:00:00Z" },
      { provider: "skyscanner", price: 14500, currency: "TWD", fetched_at: "2026-03-15T00:00:00Z" },
    ],
    lowest_price: 14500,
    highest_price: 15000,
    average_price: 14750,
  },
];

describe("useCompare", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("starts with empty state", () => {
    const { result } = renderHook(() => useCompare());
    expect(result.current.results).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("fetches compare results successfully", async () => {
    vi.mocked(api.post).mockResolvedValueOnce(mockResults);

    const { result } = renderHook(() => useCompare());

    await act(async () => {
      await result.current.compare(["flight-1"], "flight");
    });

    expect(api.post).toHaveBeenCalledWith("/compare", {
      item_ids: ["flight-1"],
      item_type: "flight",
    });
    expect(result.current.results).toEqual(mockResults);
    expect(result.current.isLoading).toBe(false);
  });

  it("handles API errors", async () => {
    vi.mocked(api.post).mockRejectedValueOnce({ detail: "Not found" });

    const { result } = renderHook(() => useCompare());

    await act(async () => {
      await result.current.compare(["bad-id"], "flight");
    });

    expect(result.current.error).toBe("Not found");
    expect(result.current.results).toEqual([]);
  });

  it("uses fallback error message for unknown errors", async () => {
    vi.mocked(api.post).mockRejectedValueOnce(new Error("network"));

    const { result } = renderHook(() => useCompare());

    await act(async () => {
      await result.current.compare(["id"], "flight");
    });

    expect(result.current.error).toBe("Comparison failed. Please try again.");
  });

  it("sets loading during request", async () => {
    let resolve: (v: unknown) => void;
    vi.mocked(api.post).mockReturnValueOnce(
      new Promise((r) => {
        resolve = r;
      })
    );

    const { result } = renderHook(() => useCompare());

    let promise: Promise<unknown>;
    act(() => {
      promise = result.current.compare(["id"], "flight");
    });

    expect(result.current.isLoading).toBe(true);

    await act(async () => {
      resolve!(mockResults);
      await promise;
    });

    expect(result.current.isLoading).toBe(false);
  });

  it("clearResults resets state", async () => {
    vi.mocked(api.post).mockResolvedValueOnce(mockResults);

    const { result } = renderHook(() => useCompare());

    await act(async () => {
      await result.current.compare(["flight-1"], "flight");
    });

    expect(result.current.results).toHaveLength(1);

    act(() => {
      result.current.clearResults();
    });

    expect(result.current.results).toEqual([]);
    expect(result.current.error).toBeNull();
  });
});
