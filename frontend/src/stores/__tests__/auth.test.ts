import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore } from "../auth";

const mockUser = {
  id: "u-1",
  email: "test@example.com",
  name: "Test User",
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
};

describe("useAuthStore", () => {
  beforeEach(() => {
    // Reset store to initial state before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      _initialized: false,
    });
  });

  it("starts with default state", () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(true);
    expect(state._initialized).toBe(false);
  });

  describe("setUser", () => {
    it("sets user and marks authenticated", () => {
      useAuthStore.getState().setUser(mockUser);
      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(true);
    });

    it("clears user and marks unauthenticated when null", () => {
      useAuthStore.getState().setUser(mockUser);
      useAuthStore.getState().setUser(null);
      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe("setLoading", () => {
    it("updates loading state", () => {
      useAuthStore.getState().setLoading(false);
      expect(useAuthStore.getState().isLoading).toBe(false);

      useAuthStore.getState().setLoading(true);
      expect(useAuthStore.getState().isLoading).toBe(true);
    });
  });

  describe("markInitialized", () => {
    it("sets _initialized to true", () => {
      useAuthStore.getState().markInitialized();
      expect(useAuthStore.getState()._initialized).toBe(true);
    });
  });

  describe("reset", () => {
    it("clears user, sets unauthenticated, stops loading, stays initialized", () => {
      useAuthStore.getState().setUser(mockUser);
      useAuthStore.getState().setLoading(true);

      useAuthStore.getState().reset();
      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
      expect(state._initialized).toBe(true);
    });
  });
});
