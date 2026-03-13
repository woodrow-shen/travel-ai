import { create } from "zustand";
import { api } from "@/lib/api";
import type { UserPreferences } from "@/types";

interface PreferencesState {
  preferences: UserPreferences | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;

  fetchPreferences: () => Promise<void>;
  updatePreferences: (data: Partial<UserPreferences>) => Promise<void>;
}

export const usePreferencesStore = create<PreferencesState>((set) => ({
  preferences: null,
  isLoading: false,
  isSaving: false,
  error: null,

  fetchPreferences: async () => {
    set({ isLoading: true, error: null });
    try {
      const prefs = await api.get<UserPreferences>("/users/preferences");
      set({ preferences: prefs, isLoading: false });
    } catch (err: unknown) {
      const message = (err as { detail?: string }).detail ?? "Failed to fetch preferences";
      set({ error: message, isLoading: false });
    }
  },

  updatePreferences: async (data: Partial<UserPreferences>) => {
    set({ isSaving: true, error: null });
    try {
      const updated = await api.patch<UserPreferences>("/users/preferences", data);
      set({ preferences: updated, isSaving: false });
    } catch (err: unknown) {
      const message = (err as { detail?: string }).detail ?? "Failed to save preferences";
      set({ error: message, isSaving: false });
      throw err;
    }
  },
}));
