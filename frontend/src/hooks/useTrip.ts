"use client";

import { useCallback } from "react";
import { api } from "@/lib/api";
import { useTripStore } from "@/stores/trip";
import type {
  TripResponse,
  CreateTripPayload,
  UpdateTripPayload,
} from "@/types";

export function useTrip() {
  const trips = useTripStore((s) => s.trips);
  const selectedTrip = useTripStore((s) => s.selectedTrip);
  const isLoading = useTripStore((s) => s.isLoading);
  const error = useTripStore((s) => s.error);
  const setTrips = useTripStore((s) => s.setTrips);
  const addTrip = useTripStore((s) => s.addTrip);
  const updateTripInStore = useTripStore((s) => s.updateTrip);
  const removeTrip = useTripStore((s) => s.removeTrip);
  const selectTrip = useTripStore((s) => s.selectTrip);
  const setLoading = useTripStore((s) => s.setLoading);
  const setError = useTripStore((s) => s.setError);

  const fetchTrips = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get<TripResponse[]>("/trips");
      setTrips(data);
    } catch (err: unknown) {
      const message =
        err && typeof err === "object" && "detail" in err
          ? (err as { detail: string }).detail
          : "Failed to load trips.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [setLoading, setTrips, setError]);

  const fetchTrip = useCallback(
    async (id: string) => {
      setLoading(true);
      try {
        const trip = await api.get<TripResponse>(`/trips/${id}`);
        selectTrip(trip);
        return trip;
      } catch (err: unknown) {
        const message =
          err && typeof err === "object" && "detail" in err
            ? (err as { detail: string }).detail
            : "Failed to load trip.";
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [setLoading, selectTrip, setError]
  );

  const createTrip = useCallback(
    async (data: CreateTripPayload) => {
      setLoading(true);
      try {
        const trip = await api.post<TripResponse>("/trips", data);
        addTrip(trip);
        return trip;
      } catch (err: unknown) {
        const message =
          err && typeof err === "object" && "detail" in err
            ? (err as { detail: string }).detail
            : "Failed to create trip.";
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [setLoading, addTrip, setError]
  );

  const updateTrip = useCallback(
    async (id: string, data: UpdateTripPayload) => {
      setLoading(true);
      try {
        const trip = await api.patch<TripResponse>(`/trips/${id}`, data);
        updateTripInStore(id, trip);
        return trip;
      } catch (err: unknown) {
        const message =
          err && typeof err === "object" && "detail" in err
            ? (err as { detail: string }).detail
            : "Failed to update trip.";
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [setLoading, updateTripInStore, setError]
  );

  const deleteTrip = useCallback(
    async (id: string) => {
      setLoading(true);
      try {
        await api.delete(`/trips/${id}`);
        removeTrip(id);
        return true;
      } catch (err: unknown) {
        const message =
          err && typeof err === "object" && "detail" in err
            ? (err as { detail: string }).detail
            : "Failed to delete trip.";
        setError(message);
        return false;
      } finally {
        setLoading(false);
      }
    },
    [setLoading, removeTrip, setError]
  );

  return {
    trips,
    selectedTrip,
    isLoading,
    error,
    fetchTrips,
    fetchTrip,
    createTrip,
    updateTrip,
    deleteTrip,
    selectTrip,
  };
}
