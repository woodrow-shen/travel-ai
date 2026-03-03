import type { ItineraryItem, TripResponse } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { formatPrice } from "@/lib/utils";

interface ItineraryViewProps {
  trip: TripResponse;
}

const typeIcons: Record<ItineraryItem["type"], string> = {
  flight: "Departure",
  hotel: "Accommodation",
  activity: "Activity",
  transfer: "Transfer",
  note: "Note",
};

const typeBadgeColors: Record<ItineraryItem["type"], string> = {
  flight: "bg-blue-100 text-blue-800",
  hotel: "bg-purple-100 text-purple-800",
  activity: "bg-green-100 text-green-800",
  transfer: "bg-orange-100 text-orange-800",
  note: "bg-gray-100 text-gray-800",
};

export function ItineraryView({ trip }: ItineraryViewProps) {
  const days = new Map<number, ItineraryItem[]>();

  for (const item of trip.itinerary) {
    const existing = days.get(item.day) ?? [];
    existing.push(item);
    days.set(item.day, existing);
  }

  const sortedDays = Array.from(days.entries()).sort(
    ([a], [b]) => a - b
  );

  if (trip.itinerary.length === 0) {
    return (
      <div className="py-8 text-center text-[var(--color-muted)]">
        <p>No itinerary items yet.</p>
        <p className="mt-1 text-sm">
          Use the AI chat to help build your itinerary.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">{trip.title}</h2>
        {trip.total_budget !== undefined && (
          <span className="text-sm text-[var(--color-muted)]">
            Budget: {formatPrice(trip.total_budget, trip.currency)}
          </span>
        )}
      </div>

      <div className="space-y-6">
        {sortedDays.map(([day, items]) => {
          const dayDate = new Date(trip.start_date);
          dayDate.setDate(dayDate.getDate() + day - 1);

          return (
            <Card key={day}>
              <CardHeader>
                <CardTitle>
                  Day {day} -{" "}
                  {dayDate.toLocaleDateString("en-US", {
                    weekday: "long",
                    month: "short",
                    day: "numeric",
                  })}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {items
                    .sort((a, b) =>
                      (a.time ?? "").localeCompare(b.time ?? "")
                    )
                    .map((item) => (
                      <div
                        key={item.id}
                        className="flex items-start gap-3 rounded-lg border border-[var(--color-border)] p-3"
                        role="listitem"
                      >
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${typeBadgeColors[item.type]}`}
                        >
                          {typeIcons[item.type]}
                        </span>

                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            {item.time && (
                              <time className="text-sm font-medium text-[var(--color-muted)]">
                                {item.time}
                              </time>
                            )}
                            <h4 className="font-medium">{item.title}</h4>
                          </div>

                          {item.description && (
                            <p className="mt-1 text-sm text-[var(--color-muted)]">
                              {item.description}
                            </p>
                          )}

                          {item.location && (
                            <p className="mt-1 text-xs text-[var(--color-muted)]">
                              Location: {item.location}
                            </p>
                          )}
                        </div>

                        {item.cost !== undefined && (
                          <span className="text-sm font-medium">
                            {formatPrice(item.cost, item.currency)}
                          </span>
                        )}
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
