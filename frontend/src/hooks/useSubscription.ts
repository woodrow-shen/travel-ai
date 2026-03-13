"use client";

import { useEffect } from "react";
import { useSubscriptionStore } from "@/stores/subscription";

export function useSubscription() {
  const emails = useSubscriptionStore((s) => s.emails);
  const subscriptions = useSubscriptionStore((s) => s.subscriptions);
  const isLoading = useSubscriptionStore((s) => s.isLoading);
  const error = useSubscriptionStore((s) => s.error);
  const fetchEmails = useSubscriptionStore((s) => s.fetchEmails);
  const addEmail = useSubscriptionStore((s) => s.addEmail);
  const deleteEmail = useSubscriptionStore((s) => s.deleteEmail);
  const fetchSubscriptions = useSubscriptionStore((s) => s.fetchSubscriptions);
  const createSubscription = useSubscriptionStore((s) => s.createSubscription);
  const toggleSubscription = useSubscriptionStore((s) => s.toggleSubscription);
  const deleteSubscription = useSubscriptionStore((s) => s.deleteSubscription);

  useEffect(() => {
    fetchEmails();
    fetchSubscriptions();
  }, [fetchEmails, fetchSubscriptions]);

  return {
    emails,
    subscriptions,
    isLoading,
    error,
    addEmail,
    deleteEmail,
    createSubscription,
    toggleSubscription,
    deleteSubscription,
  };
}
