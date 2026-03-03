"use client";

import { SearchForm } from "@/components/search/SearchForm";
import { FlightCard } from "@/components/search/FlightCard";
import { HotelCard } from "@/components/search/HotelCard";
import { useSearch } from "@/hooks/useSearch";

export default function SearchPage() {
  const {
    searchType,
    sortedFlights,
    sortedHotels,
    isLoading,
    error,
    results,
    sortBy,
    setSortBy,
    sortOrder,
    toggleSortOrder,
  } = useSearch();

  const sortOptions =
    searchType === "flight"
      ? [
          { value: "price", label: "Price" },
          { value: "duration", label: "Duration" },
        ]
      : [
          { value: "price", label: "Price" },
          { value: "rating", label: "Rating" },
        ];

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold">Search</h1>

      <div className="mb-8 rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-6">
        <SearchForm />
      </div>

      {/* Sort controls */}
      {results && (
        <div className="mb-4 flex items-center justify-between">
          <p className="text-sm text-[var(--color-muted)]">
            {results.total_results} result
            {results.total_results !== 1 ? "s" : ""} found
          </p>

          <div className="flex items-center gap-2">
            <label
              htmlFor="sort-by"
              className="text-sm text-[var(--color-muted)]"
            >
              Sort by:
            </label>
            <select
              id="sort-by"
              value={sortBy}
              onChange={(e) =>
                setSortBy(e.target.value as typeof sortBy)
              }
              className="rounded-md border border-[var(--color-border)] bg-[var(--color-card)] px-2 py-1 text-sm"
            >
              {sortOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <button
              onClick={toggleSortOrder}
              className="rounded-md border border-[var(--color-border)] px-2 py-1 text-sm hover:bg-[var(--color-border)]/30"
              aria-label={`Sort ${sortOrder === "asc" ? "descending" : "ascending"}`}
            >
              {sortOrder === "asc" ? "Low to High" : "High to Low"}
            </button>
          </div>
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="flex justify-center py-12">
          <div
            className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]"
            aria-label="Searching..."
          />
        </div>
      )}

      {/* Error state */}
      {error && (
        <div
          className="rounded-lg bg-[var(--color-error)]/10 px-4 py-3 text-sm text-[var(--color-error)]"
          role="alert"
        >
          {error}
        </div>
      )}

      {/* Results */}
      {!isLoading && !error && results && (
        <div className="space-y-4" role="list" aria-label="Search results">
          {searchType === "flight"
            ? sortedFlights.map((flight) => (
                <FlightCard key={flight.id} flight={flight} />
              ))
            : sortedHotels.map((hotel) => (
                <HotelCard key={hotel.id} hotel={hotel} />
              ))}

          {results.total_results === 0 && (
            <p className="py-8 text-center text-[var(--color-muted)]">
              No results found. Try adjusting your search criteria.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
