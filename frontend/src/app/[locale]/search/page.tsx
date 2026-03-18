"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { SearchForm } from "@/components/search/SearchForm";
import { FlightCard } from "@/components/search/FlightCard";
import { HotelCard } from "@/components/search/HotelCard";
import { useSearch } from "@/hooks/useSearch";
import { useCompareStore } from "@/stores/compare";

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
  const t = useTranslations("search");

  const toggleItem = useCompareStore((s) => s.toggleItem);
  const selectedIds = useCompareStore((s) => s.selectedIds);
  const clearSelection = useCompareStore((s) => s.clearSelection);

  const sortOptions =
    searchType === "flight"
      ? [
          { value: "price", label: t("results.price") },
          { value: "duration", label: t("results.duration") },
        ]
      : [
          { value: "price", label: t("results.price") },
          { value: "rating", label: t("results.rating") },
        ];

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold">{t("title")}</h1>

      <div className="mb-8 rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-6">
        <SearchForm />
      </div>

      {results && (
        <div className="mb-4 flex items-center justify-between">
          <p className="text-sm text-[var(--color-muted)]">
            {t("results.found", { count: results.total_results })}
          </p>

          <div className="flex items-center gap-2">
            <label htmlFor="sort-by" className="text-sm text-[var(--color-muted)]">
              {t("results.sortBy")}
            </label>
            <select
              id="sort-by"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              className="rounded-md border border-[var(--color-border)] bg-[var(--color-card)] px-2 py-1 text-sm"
            >
              {sortOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            <button
              onClick={toggleSortOrder}
              className="rounded-md border border-[var(--color-border)] px-2 py-1 text-sm hover:bg-[var(--color-border)]/30"
              aria-label={`Sort ${sortOrder === "asc" ? "descending" : "ascending"}`}
            >
              {sortOrder === "asc" ? t("results.lowToHigh") : t("results.highToLow")}
            </button>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center py-12">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]" aria-label={t("title")} />
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-[var(--color-error)]/10 px-4 py-3 text-sm text-[var(--color-error)]" role="alert">
          {error}
        </div>
      )}

      {!isLoading && !error && results && (
        <div className="space-y-4" role="list" aria-label={t("title")}>
          {searchType === "flight"
            ? sortedFlights.map((flight) => (
                <FlightCard
                  key={flight.id}
                  flight={flight}
                  onCompare={(f) => toggleItem(f.id, "flight")}
                  isSelected={selectedIds.includes(flight.id)}
                />
              ))
            : sortedHotels.map((hotel) => (
                <HotelCard
                  key={hotel.id}
                  hotel={hotel}
                  onCompare={(h) => toggleItem(h.id, "hotel")}
                  isSelected={selectedIds.includes(hotel.id)}
                />
              ))}

          {results.total_results === 0 && (
            <p className="py-8 text-center text-[var(--color-muted)]">
              {t("results.noResults")}
            </p>
          )}
        </div>
      )}

      {selectedIds.length >= 2 && (
        <div className="fixed bottom-6 left-1/2 z-40 flex -translate-x-1/2 items-center gap-3 rounded-full border border-[var(--color-border)] bg-[var(--color-card)] px-5 py-3 shadow-lg">
          <span className="text-sm font-medium">
            {t("compareBar.selected", { count: selectedIds.length })}
          </span>
          <Link
            href="/compare"
            className="rounded-full bg-[var(--color-primary)] px-4 py-1.5 text-sm font-semibold text-white hover:bg-[var(--color-primary-dark)]"
          >
            {t("compareBar.compare")}
          </Link>
          <button
            onClick={clearSelection}
            className="text-sm text-[var(--color-muted)] hover:text-[var(--color-foreground)]"
            aria-label={t("compareBar.clear")}
          >
            {t("compareBar.clear")}
          </button>
        </div>
      )}
    </div>
  );
}
