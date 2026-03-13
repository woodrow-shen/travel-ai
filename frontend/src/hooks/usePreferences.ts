"use client";

import { useEffect } from "react";
import { usePreferencesStore } from "@/stores/preferences";

export function usePreferences() {
  const preferences = usePreferencesStore((s) => s.preferences);
  const isLoading = usePreferencesStore((s) => s.isLoading);
  const isSaving = usePreferencesStore((s) => s.isSaving);
  const error = usePreferencesStore((s) => s.error);
  const fetchPreferences = usePreferencesStore((s) => s.fetchPreferences);
  const updatePreferences = usePreferencesStore((s) => s.updatePreferences);

  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  return { preferences, isLoading, isSaving, error, updatePreferences };
}
