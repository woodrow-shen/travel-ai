"use client";

import { type FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useSearch } from "@/hooks/useSearch";
import type { SearchParams, SearchType, TripType } from "@/types";
import { cn } from "@/lib/utils";

export function SearchForm() {
  const router = useRouter();
  const { searchType, setSearchType, search, currency } = useSearch();

  const [tripType, setTripType] = useState<TripType>("roundtrip");
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [departureDate, setDepartureDate] = useState("");
  const [returnDate, setReturnDate] = useState("");
  const [adults, setAdults] = useState(1);
  const [cabinClass, setCabinClass] = useState<
    "economy" | "premium_economy" | "business" | "first"
  >("economy");
  const [rooms, setRooms] = useState(1);
  const [isSearching, setIsSearching] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSearching(true);

    const params: SearchParams = {
      type: searchType,
      destination,
      departure_date: departureDate,
      adults,
      currency,
      ...(searchType === "flight"
        ? {
            origin,
            return_date: tripType === "roundtrip" ? returnDate || undefined : undefined,
            cabin_class: cabinClass,
          }
        : {
            check_in: departureDate,
            check_out: returnDate || undefined,
            rooms,
          }),
    };

    try {
      const results = await search(params);
      if (results) {
        router.push("/search");
      }
    } finally {
      setIsSearching(false);
    }
  };

  const tabs: { value: SearchType; label: string }[] = [
    { value: "flight", label: "Flights" },
    { value: "hotel", label: "Hotels" },
  ];

  return (
    <form onSubmit={handleSubmit} className="w-full" role="search" aria-label="Travel search">
      {/* Tab switcher */}
      <div className="mb-6 flex gap-1 rounded-lg bg-[var(--color-border)]/30 p-1" role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            type="button"
            role="tab"
            aria-selected={searchType === tab.value}
            className={cn(
              "flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors",
              searchType === tab.value
                ? "bg-[var(--color-card)] text-[var(--color-foreground)] shadow-sm"
                : "text-[var(--color-muted)] hover:text-[var(--color-foreground)]"
            )}
            onClick={() => setSearchType(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Trip type sub-tabs (flights only) */}
      {searchType === "flight" && (
        <div className="mb-4 flex gap-1 rounded-md bg-[var(--color-border)]/20 p-0.5 w-fit" role="tablist" aria-label="Trip type">
          {([
            { value: "roundtrip" as TripType, label: "Roundtrip" },
            { value: "one_way" as TripType, label: "One-way" },
          ]).map((tab) => (
            <button
              key={tab.value}
              type="button"
              role="tab"
              aria-selected={tripType === tab.value}
              className={cn(
                "rounded px-3 py-1 text-xs font-medium transition-colors",
                tripType === tab.value
                  ? "bg-[var(--color-card)] text-[var(--color-foreground)] shadow-sm"
                  : "text-[var(--color-muted)] hover:text-[var(--color-foreground)]"
              )}
              onClick={() => setTripType(tab.value)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {searchType === "flight" && (
          <Input
            label="From"
            placeholder="City or airport"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            required
          />
        )}

        <Input
          label={searchType === "flight" ? "To" : "Destination"}
          placeholder={searchType === "flight" ? "City or airport" : "City or hotel name"}
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          required
        />

        <Input
          label={searchType === "flight" ? "Departure" : "Check-in"}
          type="date"
          value={departureDate}
          onChange={(e) => setDepartureDate(e.target.value)}
          required
        />

        {(searchType === "hotel" || tripType === "roundtrip") && (
          <Input
            label={searchType === "flight" ? "Return" : "Check-out"}
            type="date"
            value={returnDate}
            onChange={(e) => setReturnDate(e.target.value)}
          />
        )}

        <div className="flex flex-col gap-1.5">
          <label
            htmlFor="adults"
            className="text-sm font-medium text-[var(--color-foreground)]"
          >
            Adults
          </label>
          <select
            id="adults"
            value={adults}
            onChange={(e) => setAdults(Number(e.target.value))}
            className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] px-3 py-2 text-base focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/30"
          >
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </div>

        {searchType === "flight" ? (
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="cabin-class"
              className="text-sm font-medium text-[var(--color-foreground)]"
            >
              Cabin Class
            </label>
            <select
              id="cabin-class"
              value={cabinClass}
              onChange={(e) =>
                setCabinClass(
                  e.target.value as typeof cabinClass
                )
              }
              className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] px-3 py-2 text-base focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/30"
            >
              <option value="economy">Economy</option>
              <option value="premium_economy">Premium Economy</option>
              <option value="business">Business</option>
              <option value="first">First Class</option>
            </select>
          </div>
        ) : (
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="rooms"
              className="text-sm font-medium text-[var(--color-foreground)]"
            >
              Rooms
            </label>
            <select
              id="rooms"
              value={rooms}
              onChange={(e) => setRooms(Number(e.target.value))}
              className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] px-3 py-2 text-base focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/30"
            >
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="mt-6">
        <Button type="submit" size="lg" isLoading={isSearching} className="w-full sm:w-auto min-w-[180px]">
          {isSearching
            ? (searchType === "flight" ? "Searching Flights..." : "Searching Hotels...")
            : `Search ${searchType === "flight" ? "Flights" : "Hotels"}`}
        </Button>
      </div>
    </form>
  );
}
