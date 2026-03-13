import { create } from "zustand";
import { api } from "@/lib/api";
import type { Subscription, SubscriptionEmail, SubscriptionType } from "@/types";

interface SubscriptionState {
  emails: SubscriptionEmail[];
  subscriptions: Subscription[];
  isLoading: boolean;
  error: string | null;

  fetchEmails: () => Promise<void>;
  addEmail: (email: string) => Promise<void>;
  deleteEmail: (id: string) => Promise<void>;
  fetchSubscriptions: () => Promise<void>;
  createSubscription: (
    emailId: string,
    type: SubscriptionType,
    config: Record<string, unknown>
  ) => Promise<void>;
  toggleSubscription: (id: string, isActive: boolean) => Promise<void>;
  deleteSubscription: (id: string) => Promise<void>;
}

export const useSubscriptionStore = create<SubscriptionState>((set) => ({
  emails: [],
  subscriptions: [],
  isLoading: false,
  error: null,

  fetchEmails: async () => {
    set({ isLoading: true, error: null });
    try {
      const emails = await api.get<SubscriptionEmail[]>("/subscriptions/emails");
      set({ emails, isLoading: false });
    } catch (err: unknown) {
      const message = (err as { detail?: string }).detail ?? "Failed to fetch emails";
      set({ error: message, isLoading: false });
    }
  },

  addEmail: async (email: string) => {
    set({ error: null });
    try {
      const created = await api.post<SubscriptionEmail>("/subscriptions/emails", { email });
      set((s) => ({ emails: [...s.emails, created] }));
    } catch (err: unknown) {
      const message = (err as { detail?: string }).detail ?? "Failed to add email";
      set({ error: message });
      throw err;
    }
  },

  deleteEmail: async (id: string) => {
    set({ error: null });
    try {
      await api.delete(`/subscriptions/emails/${id}`);
      set((s) => ({
        emails: s.emails.filter((e) => e.id !== id),
        subscriptions: s.subscriptions.filter((sub) => sub.email_id !== id),
      }));
    } catch (err: unknown) {
      const message = (err as { detail?: string }).detail ?? "Failed to delete email";
      set({ error: message });
    }
  },

  fetchSubscriptions: async () => {
    set({ isLoading: true, error: null });
    try {
      const subscriptions = await api.get<Subscription[]>("/subscriptions");
      set({ subscriptions, isLoading: false });
    } catch (err: unknown) {
      const message = (err as { detail?: string }).detail ?? "Failed to fetch subscriptions";
      set({ error: message, isLoading: false });
    }
  },

  createSubscription: async (
    emailId: string,
    type: SubscriptionType,
    config: Record<string, unknown>
  ) => {
    set({ error: null });
    try {
      const created = await api.post<Subscription>("/subscriptions", {
        email_id: emailId,
        type,
        config,
      });
      set((s) => ({ subscriptions: [...s.subscriptions, created] }));
    } catch (err: unknown) {
      const message = (err as { detail?: string }).detail ?? "Failed to create subscription";
      set({ error: message });
      throw err;
    }
  },

  toggleSubscription: async (id: string, isActive: boolean) => {
    set({ error: null });
    try {
      const updated = await api.patch<Subscription>(`/subscriptions/${id}`, {
        is_active: isActive,
      });
      set((s) => ({
        subscriptions: s.subscriptions.map((sub) => (sub.id === id ? updated : sub)),
      }));
    } catch (err: unknown) {
      const message = (err as { detail?: string }).detail ?? "Failed to update subscription";
      set({ error: message });
    }
  },

  deleteSubscription: async (id: string) => {
    set({ error: null });
    try {
      await api.delete(`/subscriptions/${id}`);
      set((s) => ({
        subscriptions: s.subscriptions.filter((sub) => sub.id !== id),
      }));
    } catch (err: unknown) {
      const message = (err as { detail?: string }).detail ?? "Failed to delete subscription";
      set({ error: message });
    }
  },
}));
