import { describe, it, expect, beforeEach, vi } from "vitest";
import { usePreferencesStore } from "../preferences";
import { api } from "@/lib/api";
import type { UserPreferences } from "@/types";

vi.mock("@/lib/api", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockPreferences: UserPreferences = {
  preferred_airlines: ["BR", "CI"],
  excluded_airlines: null,
  preferred_alliances: ["Star Alliance"],
  cabin_classes: ["economy", "business"],
  max_stops: 1,
  home_airports: ["TPE", "TSA"],
};

describe("usePreferencesStore", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    usePreferencesStore.setState({
      preferences: null,
      isLoading: false,
      isSaving: false,
      error: null,
    });
  });

  it("starts with default state", () => {
    const state = usePreferencesStore.getState();
    expect(state.preferences).toBeNull();
    expect(state.isLoading).toBe(false);
    expect(state.isSaving).toBe(false);
    expect(state.error).toBeNull();
  });

  describe("fetchPreferences", () => {
    it("sets preferences on success", async () => {
      vi.mocked(api.get).mockResolvedValue(mockPreferences);
      await usePreferencesStore.getState().fetchPreferences();
      const state = usePreferencesStore.getState();
      expect(state.preferences).toEqual(mockPreferences);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });

    it("sets error on failure", async () => {
      vi.mocked(api.get).mockRejectedValue({ detail: "Unauthorized" });
      await usePreferencesStore.getState().fetchPreferences();
      const state = usePreferencesStore.getState();
      expect(state.error).toBe("Unauthorized");
      expect(state.isLoading).toBe(false);
      expect(state.preferences).toBeNull();
    });

    it("uses fallback error message when detail missing", async () => {
      vi.mocked(api.get).mockRejectedValue(new Error("network"));
      await usePreferencesStore.getState().fetchPreferences();
      expect(usePreferencesStore.getState().error).toBe("Failed to fetch preferences");
    });
  });

  describe("updatePreferences", () => {
    it("sets updated preferences on success", async () => {
      const updated = { ...mockPreferences, max_stops: 2 };
      vi.mocked(api.patch).mockResolvedValue(updated);
      await usePreferencesStore.getState().updatePreferences({ max_stops: 2 });
      const state = usePreferencesStore.getState();
      expect(state.preferences).toEqual(updated);
      expect(state.isSaving).toBe(false);
      expect(state.error).toBeNull();
    });

    it("sets error and throws on failure", async () => {
      vi.mocked(api.patch).mockRejectedValue({ detail: "Validation error" });
      await expect(
        usePreferencesStore.getState().updatePreferences({ max_stops: -1 })
      ).rejects.toBeTruthy();
      const state = usePreferencesStore.getState();
      expect(state.error).toBe("Validation error");
      expect(state.isSaving).toBe(false);
    });

    it("uses fallback error message when detail missing", async () => {
      vi.mocked(api.patch).mockRejectedValue(new Error("fail"));
      await expect(
        usePreferencesStore.getState().updatePreferences({ max_stops: 0 })
      ).rejects.toBeTruthy();
      expect(usePreferencesStore.getState().error).toBe("Failed to save preferences");
    });

    it("clears previous error on new save attempt", async () => {
      usePreferencesStore.setState({ error: "old error" });
      vi.mocked(api.patch).mockResolvedValue(mockPreferences);
      await usePreferencesStore.getState().updatePreferences({});
      expect(usePreferencesStore.getState().error).toBeNull();
    });
  });
});
