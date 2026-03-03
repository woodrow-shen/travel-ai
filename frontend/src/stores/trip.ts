import { create } from "zustand";
import type { TripResponse } from "@/types";

interface TripState {
  trips: TripResponse[];
  selectedTrip: TripResponse | null;
  isLoading: boolean;
  error: string | null;

  setTrips: (trips: TripResponse[]) => void;
  addTrip: (trip: TripResponse) => void;
  updateTrip: (id: string, trip: Partial<TripResponse>) => void;
  removeTrip: (id: string) => void;
  selectTrip: (trip: TripResponse | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useTripStore = create<TripState>((set) => ({
  trips: [],
  selectedTrip: null,
  isLoading: false,
  error: null,

  setTrips: (trips) => set({ trips, error: null }),

  addTrip: (trip) =>
    set((state) => ({ trips: [...state.trips, trip], error: null })),

  updateTrip: (id, updates) =>
    set((state) => ({
      trips: state.trips.map((t) => (t.id === id ? { ...t, ...updates } : t)),
      selectedTrip:
        state.selectedTrip?.id === id
          ? { ...state.selectedTrip, ...updates }
          : state.selectedTrip,
    })),

  removeTrip: (id) =>
    set((state) => ({
      trips: state.trips.filter((t) => t.id !== id),
      selectedTrip: state.selectedTrip?.id === id ? null : state.selectedTrip,
    })),

  selectTrip: (trip) => set({ selectedTrip: trip }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error, isLoading: false }),
}));
