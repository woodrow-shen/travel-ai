"use client";

import { useEffect, useState } from "react";
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
    if (window.confirm("Are you sure you want to delete this trip?")) {
      await deleteTrip(id);
    }
  };

  const statusColors: Record<TripResponse["status"], string> = {
    planning: "bg-blue-100 text-blue-800",
    booked: "bg-green-100 text-green-800",
    in_progress: "bg-yellow-100 text-yellow-800",
    completed: "bg-gray-100 text-gray-800",
    cancelled: "bg-red-100 text-red-800",
  };

  // Show itinerary view when a trip is selected
  if (selectedTrip) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <button
          onClick={() => selectTrip(null)}
          className="mb-4 text-sm font-medium text-[var(--color-primary)] hover:underline"
        >
          Back to trips
        </button>
        <ItineraryView trip={selectedTrip} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">My Trips</h1>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "New Trip"}
        </Button>
      </div>

      {/* Create form */}
      {showForm && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Create New Trip</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              <Input
                label="Trip Title"
                placeholder="Summer Vacation"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
                required
              />
              <Input
                label="Destination"
                placeholder="Paris, France"
                value={formData.destination}
                onChange={(e) =>
                  setFormData({ ...formData, destination: e.target.value })
                }
                required
              />
              <Input
                label="Start Date"
                type="date"
                value={formData.start_date}
                onChange={(e) =>
                  setFormData({ ...formData, start_date: e.target.value })
                }
                required
              />
              <Input
                label="End Date"
                type="date"
                value={formData.end_date}
                onChange={(e) =>
                  setFormData({ ...formData, end_date: e.target.value })
                }
                required
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button onClick={handleCreate} isLoading={isLoading}>
              Create Trip
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Error */}
      {error && (
        <div
          className="mb-4 rounded-lg bg-[var(--color-error)]/10 px-4 py-3 text-sm text-[var(--color-error)]"
          role="alert"
        >
          {error}
        </div>
      )}

      {/* Loading */}
      {isLoading && trips.length === 0 && (
        <div className="flex justify-center py-12">
          <div
            className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]"
            aria-label="Loading trips..."
          />
        </div>
      )}

      {/* Trip list */}
      {!isLoading && trips.length === 0 ? (
        <div className="py-12 text-center text-[var(--color-muted)]">
          <p className="text-lg">No trips yet.</p>
          <p className="mt-1 text-sm">
            Create your first trip to start planning.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" role="list">
          {trips.map((trip) => (
            <Card key={trip.id} role="listitem">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle>{trip.title}</CardTitle>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[trip.status]}`}
                  >
                    {trip.status.replace("_", " ")}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <p className="font-medium text-[var(--color-foreground)]">
                  {trip.destination}
                </p>
                <p className="mt-1 text-sm text-[var(--color-muted)]">
                  {new Date(trip.start_date).toLocaleDateString()} -{" "}
                  {new Date(trip.end_date).toLocaleDateString()}
                </p>
                <p className="mt-1 text-sm text-[var(--color-muted)]">
                  {trip.itinerary.length} itinerary item
                  {trip.itinerary.length !== 1 ? "s" : ""}
                </p>
              </CardContent>
              <CardFooter>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => selectTrip(trip)}
                >
                  View
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(trip.id)}
                  className="text-[var(--color-error)]"
                >
                  Delete
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
