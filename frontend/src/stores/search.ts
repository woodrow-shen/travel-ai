import { create } from "zustand";
import type {
  SearchParams,
  SearchResponse,
  FlightResult,
  HotelResult,
  SearchType,
} from "@/types";

interface SearchState {
  /* Form state */
  searchType: SearchType;
  params: Partial<SearchParams>;

  /* Currency (auto-detected from IP) */
  currency: string;

  /* Results */
  results: SearchResponse | null;
  flights: FlightResult[];
  hotels: HotelResult[];

  /* Status */
  isLoading: boolean;
  error: string | null;

  /* Sort / Filter */
  sortBy: "price" | "duration" | "rating";
  sortOrder: "asc" | "desc";

  /* Actions */
  setSearchType: (type: SearchType) => void;
  setParams: (params: Partial<SearchParams>) => void;
  setCurrency: (currency: string) => void;
  setResults: (results: SearchResponse) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSortBy: (sort: SearchState["sortBy"]) => void;
  toggleSortOrder: () => void;
  reset: () => void;
}

const initialState = {
  searchType: "flight" as SearchType,
  params: { adults: 1, type: "flight" as SearchType },
  currency: "TWD",
  results: null,
  flights: [],
  hotels: [],
  isLoading: false,
  error: null,
  sortBy: "price" as const,
  sortOrder: "asc" as const,
};

export const useSearchStore = create<SearchState>((set) => ({
  ...initialState,

  setSearchType: (type) =>
    set({ searchType: type, params: { adults: 1, type } }),

  setParams: (params) =>
    set((state) => ({ params: { ...state.params, ...params } })),

  setCurrency: (currency) => set({ currency }),

  setResults: (results) =>
    set({
      results,
      flights: results.flights ?? [],
      hotels: results.hotels ?? [],
      error: null,
    }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error, isLoading: false }),

  setSortBy: (sortBy) => set({ sortBy }),

  toggleSortOrder: () =>
    set((state) => ({
      sortOrder: state.sortOrder === "asc" ? "desc" : "asc",
    })),

  reset: () => set(initialState),
}));
