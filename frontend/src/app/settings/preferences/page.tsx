"use client";

import { useAuth } from "@/hooks/useAuth";

export default function PreferencesPage() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <p className="text-[var(--color-muted)]">Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <p className="text-[var(--color-muted)]">Please sign in to manage preferences.</p>
      </div>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="mb-8 text-2xl font-bold">Preferences</h1>
      <p className="text-sm text-[var(--color-muted)]">
        User preference settings coming soon.
      </p>
    </main>
  );
}
