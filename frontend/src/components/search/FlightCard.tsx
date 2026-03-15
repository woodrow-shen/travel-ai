"use client";

import { useState } from "react";
import type { FlightResult } from "@/types";
import { Card, CardContent, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { formatPrice, formatDuration } from "@/lib/utils";
import { api } from "@/lib/api";

interface FlightCardProps {
  flight: FlightResult;
  onSelect?: (flight: FlightResult) => void;
  onCompare?: (flight: FlightResult) => void;
  isSelected?: boolean;
}

interface BookingOption {
  airline_code: string;
  flight_number: string;
  airline_name: string;
  price: number | null;
  booking_link: string;
}

interface BookingDetailsResponse {
  options: BookingOption[];
}

export function FlightCard({
  flight,
  onSelect,
  onCompare,
  isSelected = false,
}: FlightCardProps) {
  const [bookingLoading, setBookingLoading] = useState(false);

  const outbound = flight.outbound_segments;
  const firstSegment = outbound[0];
  const lastSegment = outbound[outbound.length - 1];

  const returnSegs = flight.return_segments;
  const returnFirst = returnSegs?.[0];
  const returnLast = returnSegs?.[returnSegs.length - 1];

  const hasDirectBookingUrl = !!flight.booking_url;
  const hasBookingToken = !!flight.booking_token;
  const showBookNow = hasDirectBookingUrl || hasBookingToken;

  async function handleBookNow() {
    if (flight.booking_url) {
      window.open(flight.booking_url, "_blank", "noopener,noreferrer");
      return;
    }

    if (!flight.booking_token) return;

    setBookingLoading(true);
    try {
      const res = await api.post<BookingDetailsResponse>(
        "/search/booking-details",
        {
          booking_token: flight.booking_token,
          currency: flight.currency || "TWD",
        }
      );

      const firstOption = res.options?.[0];
      if (firstOption?.booking_link) {
        window.open(firstOption.booking_link, "_blank", "noopener,noreferrer");
      }
    } catch {
      // Silently fail — booking link unavailable
    } finally {
      setBookingLoading(false);
    }
  }

  return (
    <Card
      className={isSelected ? "ring-2 ring-[var(--color-primary)]" : ""}
      role="article"
      aria-label={`Flight from ${firstSegment?.departure_airport} to ${lastSegment?.arrival_airport}, ${formatPrice(flight.price, flight.currency)}`}
    >
      <CardContent>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          {/* Outbound + Return legs */}
          <div className="flex-1">
            {/* Outbound leg */}
            <div className="flex items-center gap-2">
              {firstSegment?.airline_logo && (
                <img
                  src={firstSegment.airline_logo}
                  alt=""
                  className="h-8 w-8 rounded"
                  aria-hidden="true"
                />
              )}
              <span className="font-medium">{firstSegment?.airline}</span>
              <span className="text-sm text-[var(--color-muted)]">
                {firstSegment?.flight_number}
              </span>
            </div>

            <div className="mt-2 flex items-center gap-3">
              <div className="text-center">
                <p className="text-lg font-semibold">
                  {firstSegment?.departure_time?.slice(11, 16)}
                </p>
                <p className="text-sm text-[var(--color-muted)]">
                  {firstSegment?.departure_airport}
                </p>
              </div>

              <div className="flex flex-1 flex-col items-center">
                <span className="text-xs text-[var(--color-muted)]">
                  {formatDuration(flight.total_duration_minutes)}
                </span>
                <div className="relative my-1 h-px w-full bg-[var(--color-border)]">
                  <div className="absolute left-0 top-1/2 h-2 w-2 -translate-y-1/2 rounded-full bg-[var(--color-muted)]" />
                  <div className="absolute right-0 top-1/2 h-2 w-2 -translate-y-1/2 rounded-full bg-[var(--color-muted)]" />
                </div>
                <span className="text-xs text-[var(--color-muted)]">
                  {flight.stops === 0
                    ? "Direct"
                    : `${flight.stops} stop${flight.stops > 1 ? "s" : ""}`}
                </span>
              </div>

              <div className="text-center">
                <p className="text-lg font-semibold">
                  {lastSegment?.arrival_time?.slice(11, 16)}
                </p>
                <p className="text-sm text-[var(--color-muted)]">
                  {lastSegment?.arrival_airport}
                </p>
              </div>
            </div>

            {/* Return leg */}
            {returnSegs && returnSegs.length > 0 && returnFirst && returnLast && (
              <>
                <div className="my-3 border-t border-dashed border-[var(--color-border)]" />
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium uppercase text-[var(--color-muted)]">Return</span>
                  <span className="font-medium">{returnFirst.airline}</span>
                  <span className="text-sm text-[var(--color-muted)]">
                    {returnFirst.flight_number}
                  </span>
                </div>
                <div className="mt-2 flex items-center gap-3">
                  <div className="text-center">
                    <p className="text-lg font-semibold">
                      {returnFirst.departure_time?.slice(11, 16)}
                    </p>
                    <p className="text-sm text-[var(--color-muted)]">
                      {returnFirst.departure_airport}
                    </p>
                  </div>

                  <div className="flex flex-1 flex-col items-center">
                    <span className="text-xs text-[var(--color-muted)]">
                      {formatDuration(
                        returnSegs.reduce((sum, s) => sum + s.duration_minutes, 0)
                      )}
                    </span>
                    <div className="relative my-1 h-px w-full bg-[var(--color-border)]">
                      <div className="absolute left-0 top-1/2 h-2 w-2 -translate-y-1/2 rounded-full bg-[var(--color-muted)]" />
                      <div className="absolute right-0 top-1/2 h-2 w-2 -translate-y-1/2 rounded-full bg-[var(--color-muted)]" />
                    </div>
                    <span className="text-xs text-[var(--color-muted)]">
                      {returnSegs.length <= 1
                        ? "Direct"
                        : `${returnSegs.length - 1} stop${returnSegs.length - 1 > 1 ? "s" : ""}`}
                    </span>
                  </div>

                  <div className="text-center">
                    <p className="text-lg font-semibold">
                      {returnLast.arrival_time?.slice(11, 16)}
                    </p>
                    <p className="text-sm text-[var(--color-muted)]">
                      {returnLast.arrival_airport}
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Price */}
          <div className="text-right sm:min-w-[120px]">
            <p className="text-2xl font-bold text-[var(--color-primary)]">
              {formatPrice(flight.price, flight.currency)}
            </p>
            <p className="text-sm text-[var(--color-muted)]">
              {flight.provider}
            </p>
            {returnSegs && returnSegs.length > 0 && (
              <p className="text-xs text-[var(--color-muted)]">roundtrip</p>
            )}
          </div>
        </div>
      </CardContent>

      <CardFooter>
        {onSelect && (
          <Button size="sm" onClick={() => onSelect(flight)}>
            Select
          </Button>
        )}
        {onCompare && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onCompare(flight)}
          >
            Compare
          </Button>
        )}
        {showBookNow && (
          <button
            onClick={handleBookNow}
            disabled={bookingLoading}
            className="ml-auto text-sm text-[var(--color-primary)] hover:underline disabled:opacity-50"
          >
            {bookingLoading ? "Loading..." : "Book now"}
          </button>
        )}
      </CardFooter>
    </Card>
  );
}
