"use client";

import { useCallback, useEffect } from "react";
import { api } from "@/lib/api";
import { useSearchStore } from "@/stores/search";
import type { SearchParams, SearchResponse } from "@/types";

export function useSearch() {
  const searchType = useSearchStore((s) => s.searchType);
  const params = useSearchStore((s) => s.params);
  const setCurrency = useSearchStore((s) => s.setCurrency);
  const setLoading = useSearchStore((s) => s.setLoading);
  const setError = useSearchStore((s) => s.setError);
  const setResults = useSearchStore((s) => s.setResults);
  const flights = useSearchStore((s) => s.flights);
  const hotels = useSearchStore((s) => s.hotels);
  const sortBy = useSearchStore((s) => s.sortBy);
  const sortOrder = useSearchStore((s) => s.sortOrder);
  const isLoading = useSearchStore((s) => s.isLoading);
  const error = useSearchStore((s) => s.error);
  const currency = useSearchStore((s) => s.currency);
  const results = useSearchStore((s) => s.results);
  const setSearchType = useSearchStore((s) => s.setSearchType);
  const setParams = useSearchStore((s) => s.setParams);
  const setSortBy = useSearchStore((s) => s.setSortBy);
  const toggleSortOrder = useSearchStore((s) => s.toggleSortOrder);
  const reset = useSearchStore((s) => s.reset);

  // Auto-detect currency from IP on first mount
  useEffect(() => {
    let cancelled = false;
    api
      .get<{ currency: string; country: string }>("/geo/currency")
      .then((data) => {
        if (!cancelled && data.currency) {
          setCurrency(data.currency);
        }
      })
      .catch(() => {
        // Fallback: keep default TWD
      });
    return () => {
      cancelled = true;
    };
  }, [setCurrency]);

  const search = useCallback(
    async (params: SearchParams) => {
      setLoading(true);
      setError(null);

      try {
        const endpoint =
          params.type === "flight" ? "/search/flights" : "/search/hotels";
        const data = await api.post<SearchResponse>(endpoint, params);
        setResults(data);
        return data;
      } catch (err: unknown) {
        const message =
          err && typeof err === "object" && "detail" in err
            ? (err as { detail: string }).detail
            : "Search failed. Please try again.";
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [setLoading, setError, setResults]
  );

  const sortedFlights = [...flights].sort((a, b) => {
    const multiplier = sortOrder === "asc" ? 1 : -1;
    switch (sortBy) {
      case "price":
        return (a.price - b.price) * multiplier;
      case "duration":
        return (
          (a.total_duration_minutes - b.total_duration_minutes) * multiplier
        );
      default:
        return (a.price - b.price) * multiplier;
    }
  });

  const sortedHotels = [...hotels].sort((a, b) => {
    const multiplier = sortOrder === "asc" ? 1 : -1;
    switch (sortBy) {
      case "price":
        return (a.price_per_night - b.price_per_night) * multiplier;
      case "rating":
        return ((a.user_rating ?? 0) - (b.user_rating ?? 0)) * multiplier;
      default:
        return (a.price_per_night - b.price_per_night) * multiplier;
    }
  });

  return {
    searchType,
    params,
    flights,
    hotels,
    sortBy,
    sortOrder,
    isLoading,
    error,
    currency,
    results,
    setSearchType,
    setParams,
    setCurrency,
    setLoading,
    setError,
    setSortBy,
    toggleSortOrder,
    reset,
    search,
    sortedFlights,
    sortedHotels,
  };
}
