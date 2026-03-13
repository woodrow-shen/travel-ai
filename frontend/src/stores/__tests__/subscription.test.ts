import { describe, it, expect, beforeEach, vi } from "vitest";
import { useSubscriptionStore } from "../subscription";
import { api } from "@/lib/api";
import type { SubscriptionEmail, Subscription } from "@/types";

vi.mock("@/lib/api", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockEmail: SubscriptionEmail = {
  id: "e-1",
  email: "test@example.com",
  is_verified: true,
  verified_at: "2026-01-01T00:00:00Z",
  created_at: "2026-01-01T00:00:00Z",
};

const mockEmail2: SubscriptionEmail = {
  id: "e-2",
  email: "other@example.com",
  is_verified: false,
  verified_at: null,
  created_at: "2026-01-02T00:00:00Z",
};

const mockSubscription: Subscription = {
  id: "sub-1",
  email_id: "e-1",
  type: "price_drop",
  config: { origin: "TPE", destination: "NRT" },
  is_active: true,
  last_sent_at: null,
  created_at: "2026-01-01T00:00:00Z",
};

const mockSubscription2: Subscription = {
  id: "sub-2",
  email_id: "e-2",
  type: "bug_fare",
  config: {},
  is_active: true,
  last_sent_at: null,
  created_at: "2026-01-02T00:00:00Z",
};

describe("useSubscriptionStore", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useSubscriptionStore.setState({
      emails: [],
      subscriptions: [],
      isLoading: false,
      error: null,
    });
  });

  it("starts with default state", () => {
    const state = useSubscriptionStore.getState();
    expect(state.emails).toEqual([]);
    expect(state.subscriptions).toEqual([]);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  describe("fetchEmails", () => {
    it("sets emails on success", async () => {
      vi.mocked(api.get).mockResolvedValue([mockEmail, mockEmail2]);
      await useSubscriptionStore.getState().fetchEmails();
      const state = useSubscriptionStore.getState();
      expect(state.emails).toEqual([mockEmail, mockEmail2]);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });

    it("sets error on failure", async () => {
      vi.mocked(api.get).mockRejectedValue({ detail: "Unauthorized" });
      await useSubscriptionStore.getState().fetchEmails();
      const state = useSubscriptionStore.getState();
      expect(state.error).toBe("Unauthorized");
      expect(state.isLoading).toBe(false);
      expect(state.emails).toEqual([]);
    });

    it("uses fallback error message when detail missing", async () => {
      vi.mocked(api.get).mockRejectedValue(new Error("network"));
      await useSubscriptionStore.getState().fetchEmails();
      expect(useSubscriptionStore.getState().error).toBe("Failed to fetch emails");
    });
  });

  describe("addEmail", () => {
    it("appends new email on success", async () => {
      useSubscriptionStore.setState({ emails: [mockEmail] });
      vi.mocked(api.post).mockResolvedValue(mockEmail2);
      await useSubscriptionStore.getState().addEmail("other@example.com");
      const state = useSubscriptionStore.getState();
      expect(state.emails).toHaveLength(2);
      expect(state.emails[1]).toEqual(mockEmail2);
      expect(state.error).toBeNull();
    });

    it("sets error and throws on failure", async () => {
      vi.mocked(api.post).mockRejectedValue({ detail: "Email exists" });
      await expect(useSubscriptionStore.getState().addEmail("dup@example.com")).rejects.toBeTruthy();
      expect(useSubscriptionStore.getState().error).toBe("Email exists");
    });

    it("uses fallback error message when detail missing", async () => {
      vi.mocked(api.post).mockRejectedValue(new Error("fail"));
      await expect(useSubscriptionStore.getState().addEmail("x@y.com")).rejects.toBeTruthy();
      expect(useSubscriptionStore.getState().error).toBe("Failed to add email");
    });
  });

  describe("deleteEmail", () => {
    it("removes email and cascades subscriptions on success", async () => {
      useSubscriptionStore.setState({
        emails: [mockEmail, mockEmail2],
        subscriptions: [mockSubscription, mockSubscription2],
      });
      vi.mocked(api.delete).mockResolvedValue(undefined);
      await useSubscriptionStore.getState().deleteEmail("e-1");
      const state = useSubscriptionStore.getState();
      expect(state.emails).toEqual([mockEmail2]);
      expect(state.subscriptions).toEqual([mockSubscription2]);
    });

    it("sets error on failure", async () => {
      useSubscriptionStore.setState({ emails: [mockEmail] });
      vi.mocked(api.delete).mockRejectedValue({ detail: "Not found" });
      await useSubscriptionStore.getState().deleteEmail("e-1");
      expect(useSubscriptionStore.getState().error).toBe("Not found");
      // Email should still be present (optimistic removal didn't happen)
      expect(useSubscriptionStore.getState().emails).toEqual([mockEmail]);
    });
  });

  describe("fetchSubscriptions", () => {
    it("sets subscriptions on success", async () => {
      vi.mocked(api.get).mockResolvedValue([mockSubscription]);
      await useSubscriptionStore.getState().fetchSubscriptions();
      const state = useSubscriptionStore.getState();
      expect(state.subscriptions).toEqual([mockSubscription]);
      expect(state.isLoading).toBe(false);
    });

    it("sets error on failure", async () => {
      vi.mocked(api.get).mockRejectedValue({ detail: "Server error" });
      await useSubscriptionStore.getState().fetchSubscriptions();
      expect(useSubscriptionStore.getState().error).toBe("Server error");
      expect(useSubscriptionStore.getState().isLoading).toBe(false);
    });
  });

  describe("createSubscription", () => {
    it("appends subscription on success", async () => {
      useSubscriptionStore.setState({ subscriptions: [mockSubscription] });
      vi.mocked(api.post).mockResolvedValue(mockSubscription2);
      await useSubscriptionStore.getState().createSubscription("e-2", "bug_fare", {});
      expect(useSubscriptionStore.getState().subscriptions).toHaveLength(2);
      expect(useSubscriptionStore.getState().subscriptions[1]).toEqual(mockSubscription2);
    });

    it("sets error and throws on failure", async () => {
      vi.mocked(api.post).mockRejectedValue({ detail: "Invalid config" });
      await expect(
        useSubscriptionStore.getState().createSubscription("e-1", "price_drop", {})
      ).rejects.toBeTruthy();
      expect(useSubscriptionStore.getState().error).toBe("Invalid config");
    });

    it("uses fallback error message when detail missing", async () => {
      vi.mocked(api.post).mockRejectedValue(new Error("fail"));
      await expect(
        useSubscriptionStore.getState().createSubscription("e-1", "deal_digest", {})
      ).rejects.toBeTruthy();
      expect(useSubscriptionStore.getState().error).toBe("Failed to create subscription");
    });
  });

  describe("toggleSubscription", () => {
    it("updates is_active in local state on success", async () => {
      useSubscriptionStore.setState({ subscriptions: [mockSubscription] });
      const updated = { ...mockSubscription, is_active: false };
      vi.mocked(api.patch).mockResolvedValue(updated);
      await useSubscriptionStore.getState().toggleSubscription("sub-1", false);
      expect(useSubscriptionStore.getState().subscriptions[0].is_active).toBe(false);
    });

    it("sets error on failure", async () => {
      useSubscriptionStore.setState({ subscriptions: [mockSubscription] });
      vi.mocked(api.patch).mockRejectedValue({ detail: "Toggle failed" });
      await useSubscriptionStore.getState().toggleSubscription("sub-1", false);
      expect(useSubscriptionStore.getState().error).toBe("Toggle failed");
      // Original state preserved
      expect(useSubscriptionStore.getState().subscriptions[0].is_active).toBe(true);
    });
  });

  describe("deleteSubscription", () => {
    it("removes subscription from list on success", async () => {
      useSubscriptionStore.setState({ subscriptions: [mockSubscription, mockSubscription2] });
      vi.mocked(api.delete).mockResolvedValue(undefined);
      await useSubscriptionStore.getState().deleteSubscription("sub-1");
      expect(useSubscriptionStore.getState().subscriptions).toEqual([mockSubscription2]);
    });

    it("sets error on failure", async () => {
      useSubscriptionStore.setState({ subscriptions: [mockSubscription] });
      vi.mocked(api.delete).mockRejectedValue({ detail: "Delete failed" });
      await useSubscriptionStore.getState().deleteSubscription("sub-1");
      expect(useSubscriptionStore.getState().error).toBe("Delete failed");
      expect(useSubscriptionStore.getState().subscriptions).toEqual([mockSubscription]);
    });
  });
});
