import { describe, it, expect, beforeEach } from "vitest";
import { useSearchStore } from "../search";
import type { SearchResponse } from "@/types";

const mockFlightResponse: SearchResponse = {
  search_id: "s-1",
  type: "flight",
  flights: [
    {
      id: "f-1",
      provider: "amadeus",
      price: 15000,
      currency: "TWD",
      outbound_segments: [],
      total_duration_minutes: 180,
      stops: 0,
    },
  ],
  total_results: 1,
  search_params: { type: "flight", destination: "NRT", departure_date: "2026-04-01", adults: 1 },
  created_at: "2026-03-13T00:00:00Z",
};

const mockHotelResponse: SearchResponse = {
  search_id: "s-2",
  type: "hotel",
  hotels: [
    {
      id: "h-1",
      provider: "kiwi",
      name: "Test Hotel",
      address: "Tokyo",
      star_rating: 4,
      price_per_night: 3000,
      total_price: 9000,
      currency: "TWD",
      amenities: ["wifi"],
      images: [],
    },
  ],
  total_results: 1,
  search_params: { type: "hotel", destination: "TYO", departure_date: "2026-04-01", adults: 1 },
  created_at: "2026-03-13T00:00:00Z",
};

const initialState = {
  searchType: "flight" as const,
  params: { adults: 1, type: "flight" as const },
  currency: "TWD",
  results: null,
  flights: [],
  hotels: [],
  isLoading: false,
  error: null,
  sortBy: "price" as const,
  sortOrder: "asc" as const,
};

describe("useSearchStore", () => {
  beforeEach(() => {
    useSearchStore.setState(initialState);
  });

  it("starts with default state", () => {
    const state = useSearchStore.getState();
    expect(state.searchType).toBe("flight");
    expect(state.params).toEqual({ adults: 1, type: "flight" });
    expect(state.currency).toBe("TWD");
    expect(state.results).toBeNull();
    expect(state.flights).toEqual([]);
    expect(state.hotels).toEqual([]);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.sortBy).toBe("price");
    expect(state.sortOrder).toBe("asc");
  });

  describe("setSearchType", () => {
    it("updates type and resets params", () => {
      useSearchStore.getState().setSearchType("hotel");
      const state = useSearchStore.getState();
      expect(state.searchType).toBe("hotel");
      expect(state.params).toEqual({ adults: 1, type: "hotel" });
    });

    it("switches back to flight", () => {
      useSearchStore.getState().setSearchType("hotel");
      useSearchStore.getState().setSearchType("flight");
      const state = useSearchStore.getState();
      expect(state.searchType).toBe("flight");
      expect(state.params).toEqual({ adults: 1, type: "flight" });
    });
  });

  describe("setParams", () => {
    it("merges into existing params", () => {
      useSearchStore.getState().setParams({ origin: "TPE" });
      const state = useSearchStore.getState();
      expect(state.params).toEqual({ adults: 1, type: "flight", origin: "TPE" });
    });

    it("overwrites existing param values", () => {
      useSearchStore.getState().setParams({ adults: 3 });
      expect(useSearchStore.getState().params.adults).toBe(3);
    });
  });

  describe("setCurrency", () => {
    it("sets currency", () => {
      useSearchStore.getState().setCurrency("USD");
      expect(useSearchStore.getState().currency).toBe("USD");
    });
  });

  describe("setResults", () => {
    it("extracts flights from response", () => {
      useSearchStore.getState().setResults(mockFlightResponse);
      const state = useSearchStore.getState();
      expect(state.results).toEqual(mockFlightResponse);
      expect(state.flights).toHaveLength(1);
      expect(state.flights[0].id).toBe("f-1");
      expect(state.hotels).toEqual([]);
      expect(state.error).toBeNull();
    });

    it("extracts hotels from response", () => {
      useSearchStore.getState().setResults(mockHotelResponse);
      const state = useSearchStore.getState();
      expect(state.hotels).toHaveLength(1);
      expect(state.hotels[0].id).toBe("h-1");
      expect(state.flights).toEqual([]);
    });

    it("clears previous error on new results", () => {
      useSearchStore.setState({ error: "previous error" });
      useSearchStore.getState().setResults(mockFlightResponse);
      expect(useSearchStore.getState().error).toBeNull();
    });

    it("defaults missing arrays to empty", () => {
      const minimal: SearchResponse = {
        search_id: "s-3",
        type: "flight",
        total_results: 0,
        search_params: { type: "flight", destination: "NRT", departure_date: "2026-04-01", adults: 1 },
        created_at: "2026-03-13T00:00:00Z",
      };
      useSearchStore.getState().setResults(minimal);
      const state = useSearchStore.getState();
      expect(state.flights).toEqual([]);
      expect(state.hotels).toEqual([]);
    });
  });

  describe("setLoading", () => {
    it("toggles loading state", () => {
      useSearchStore.getState().setLoading(true);
      expect(useSearchStore.getState().isLoading).toBe(true);

      useSearchStore.getState().setLoading(false);
      expect(useSearchStore.getState().isLoading).toBe(false);
    });
  });

  describe("setError", () => {
    it("sets error message and clears loading", () => {
      useSearchStore.setState({ isLoading: true });
      useSearchStore.getState().setError("Something went wrong");
      const state = useSearchStore.getState();
      expect(state.error).toBe("Something went wrong");
      expect(state.isLoading).toBe(false);
    });

    it("clears error when set to null", () => {
      useSearchStore.setState({ error: "old error" });
      useSearchStore.getState().setError(null);
      expect(useSearchStore.getState().error).toBeNull();
    });
  });

  describe("setSortBy", () => {
    it("changes sort field", () => {
      useSearchStore.getState().setSortBy("duration");
      expect(useSearchStore.getState().sortBy).toBe("duration");

      useSearchStore.getState().setSortBy("rating");
      expect(useSearchStore.getState().sortBy).toBe("rating");
    });
  });

  describe("toggleSortOrder", () => {
    it("flips asc to desc", () => {
      useSearchStore.getState().toggleSortOrder();
      expect(useSearchStore.getState().sortOrder).toBe("desc");
    });

    it("flips desc back to asc", () => {
      useSearchStore.getState().toggleSortOrder();
      useSearchStore.getState().toggleSortOrder();
      expect(useSearchStore.getState().sortOrder).toBe("asc");
    });
  });

  describe("reset", () => {
    it("returns to initial state", () => {
      // Mutate everything
      useSearchStore.getState().setSearchType("hotel");
      useSearchStore.getState().setCurrency("USD");
      useSearchStore.getState().setResults(mockHotelResponse);
      useSearchStore.getState().setLoading(true);
      useSearchStore.getState().setError("err");
      useSearchStore.getState().setSortBy("duration");
      useSearchStore.getState().toggleSortOrder();

      useSearchStore.getState().reset();
      const state = useSearchStore.getState();
      expect(state.searchType).toBe("flight");
      expect(state.params).toEqual({ adults: 1, type: "flight" });
      expect(state.currency).toBe("TWD");
      expect(state.results).toBeNull();
      expect(state.flights).toEqual([]);
      expect(state.hotels).toEqual([]);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.sortBy).toBe("price");
      expect(state.sortOrder).toBe("asc");
    });
  });
});
