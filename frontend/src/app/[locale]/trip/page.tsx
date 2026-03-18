"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useTrip } from "@/hooks/useTrip";
import { ItineraryView } from "@/components/itinerary/ItineraryView";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/Card";
import type { CreateTripPayload, TripResponse } from "@/types";

export default function TripPage() {
  const {
    trips,
    selectedTrip,
    isLoading,
    error,
    fetchTrips,
    createTrip,
    deleteTrip,
    selectTrip,
  } = useTrip();
  const t = useTranslations("trip");
  const tc = useTranslations("common");

  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<CreateTripPayload>({
    title: "",
    destination: "",
    start_date: "",
    end_date: "",
  });

  useEffect(() => {
    fetchTrips();
  }, [fetchTrips]);

  const handleCreate = async () => {
    if (!formData.title || !formData.destination || !formData.start_date || !formData.end_date)
      return;

    const trip = await createTrip(formData);
    if (trip) {
      setShowForm(false);
      setFormData({ title: "", destination: "", start_date: "", end_date: "" });
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm(t("confirmDelete"))) {
      await deleteTrip(id);
    }
  };

  const statusColors: Record<TripResponse["status"], string> = {
    planning: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
    booked: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    in_progress: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
    completed: "bg-gray-100 text-gray-800 dark:bg-gray-700/30 dark:text-gray-300",
    cancelled: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  };

  if (selectedTrip) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <button
          onClick={() => selectTrip(null)}
          className="mb-4 text-sm font-medium text-[var(--color-primary)] hover:underline"
        >
          {t("backToTrips")}
        </button>
        <ItineraryView trip={selectedTrip} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("title")}</h1>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? tc("cancel") : t("newTrip")}
        </Button>
      </div>

      {showForm && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>{t("form.title")}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              <Input
                label={t("form.tripTitle")}
                placeholder={t("form.tripTitlePlaceholder")}
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
              <Input
                label={t("form.destination")}
                placeholder={t("form.destinationPlaceholder")}
                value={formData.destination}
                onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                required
              />
              <Input
                label={t("form.startDate")}
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                required
              />
              <Input
                label={t("form.endDate")}
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                required
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button onClick={handleCreate} isLoading={isLoading}>
              {t("form.createTrip")}
            </Button>
          </CardFooter>
        </Card>
      )}

      {error && (
        <div className="mb-4 rounded-lg bg-[var(--color-error)]/10 px-4 py-3 text-sm text-[var(--color-error)]" role="alert">
          {error}
        </div>
      )}

      {isLoading && trips.length === 0 && (
        <div className="flex justify-center py-12">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]" aria-label={tc("loading")} />
        </div>
      )}

      {!isLoading && trips.length === 0 ? (
        <div className="py-12 text-center text-[var(--color-muted)]">
          <p className="text-lg">{t("noTrips")}</p>
          <p className="mt-1 text-sm">{t("noTripsHint")}</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" role="list">
          {trips.map((trip) => (
            <Card key={trip.id} role="listitem">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle>{trip.title}</CardTitle>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[trip.status]}`}>
                    {t(`status.${trip.status}`)}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <p className="font-medium text-[var(--color-foreground)]">{trip.destination}</p>
                <p className="mt-1 text-sm text-[var(--color-muted)]">
                  {new Date(trip.start_date).toLocaleDateString()} - {new Date(trip.end_date).toLocaleDateString()}
                </p>
                <p className="mt-1 text-sm text-[var(--color-muted)]">
                  {t("itinerary.items", { count: trip.itinerary.length })}
                </p>
              </CardContent>
              <CardFooter>
                <Button variant="outline" size="sm" onClick={() => selectTrip(trip)}>
                  {tc("view")}
                </Button>
                <Button variant="ghost" size="sm" onClick={() => handleDelete(trip.id)} className="text-[var(--color-error)]">
                  {tc("delete")}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
