"use client";

import { useTranslations } from "next-intl";
import type { HotelResult } from "@/types";
import { Card, CardContent, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { formatPrice } from "@/lib/utils";

interface HotelCardProps {
  hotel: HotelResult;
  onSelect?: (hotel: HotelResult) => void;
  onCompare?: (hotel: HotelResult) => void;
  isSelected?: boolean;
}

export function HotelCard({
  hotel,
  onSelect,
  onCompare,
  isSelected = false,
}: HotelCardProps) {
  const stars = Array.from({ length: 5 }, (_, i) => i < hotel.star_rating);
  const t = useTranslations("search.hotelCard");
  const tc = useTranslations("common");

  return (
    <Card
      className={isSelected ? "ring-2 ring-[var(--color-primary)]" : ""}
      role="article"
      aria-label={`${hotel.name}, ${hotel.star_rating} stars, ${formatPrice(hotel.price_per_night, hotel.currency)} ${t("perNight")}`}
    >
      <CardContent>
        <div className="flex flex-col gap-4 sm:flex-row">
          {/* Image */}
          {hotel.images.length > 0 && (
            <div className="h-40 w-full overflow-hidden rounded-lg sm:h-auto sm:w-48 sm:flex-shrink-0">
              <img
                src={hotel.images[0]}
                alt={`${hotel.name} exterior`}
                className="h-full w-full object-cover"
                loading="lazy"
              />
            </div>
          )}

          {/* Details */}
          <div className="flex flex-1 flex-col justify-between">
            <div>
              <h3 className="text-lg font-semibold">{hotel.name}</h3>

              <div className="mt-1 flex items-center gap-1" aria-label={`${hotel.star_rating} out of 5 stars`}>
                {stars.map((filled, i) => (
                  <svg
                    key={i}
                    className={`h-4 w-4 ${filled ? "text-[var(--color-accent)]" : "text-[var(--color-border)]"}`}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    aria-hidden="true"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>

              <p className="mt-1 text-sm text-[var(--color-muted)]">
                {hotel.address}
              </p>

              {hotel.user_rating !== undefined && (
                <div className="mt-2 flex items-center gap-2">
                  <span className="rounded bg-[var(--color-primary)] px-2 py-0.5 text-sm font-medium text-white">
                    {hotel.user_rating.toFixed(1)}
                  </span>
                  {hotel.review_count !== undefined && (
                    <span className="text-sm text-[var(--color-muted)]">
                      {t("reviews", { count: hotel.review_count.toLocaleString() })}
                    </span>
                  )}
                </div>
              )}

              {hotel.amenities.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {hotel.amenities.slice(0, 5).map((amenity) => (
                    <span
                      key={amenity}
                      className="rounded-full bg-[var(--color-border)]/50 px-2 py-0.5 text-xs text-[var(--color-muted)]"
                    >
                      {amenity}
                    </span>
                  ))}
                  {hotel.amenities.length > 5 && (
                    <span className="rounded-full bg-[var(--color-border)]/50 px-2 py-0.5 text-xs text-[var(--color-muted)]">
                      {t("more", { count: hotel.amenities.length - 5 })}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Price */}
          <div className="text-right sm:min-w-[140px]">
            <p className="text-2xl font-bold text-[var(--color-primary)]">
              {formatPrice(hotel.price_per_night, hotel.currency)}
            </p>
            <p className="text-sm text-[var(--color-muted)]">{t("perNight")}</p>
            <p className="mt-1 text-sm text-[var(--color-muted)]">
              {t("total", { price: formatPrice(hotel.total_price, hotel.currency) })}
            </p>
            <p className="text-xs text-[var(--color-muted)]">{hotel.provider}</p>
            {hotel.cancellation_policy && (
              <p className="mt-1 text-xs text-[var(--color-success)]">
                {hotel.cancellation_policy}
              </p>
            )}
          </div>
        </div>
      </CardContent>

      <CardFooter>
        {onSelect && (
          <Button size="sm" onClick={() => onSelect(hotel)}>
            {tc("select")}
          </Button>
        )}
        {onCompare && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onCompare(hotel)}
          >
            {tc("compare")}
          </Button>
        )}
        {hotel.booking_url && (
          <a
            href={hotel.booking_url}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-auto text-sm text-[var(--color-primary)] hover:underline"
          >
            {t("bookNow")}
          </a>
        )}
      </CardFooter>
    </Card>
  );
}
