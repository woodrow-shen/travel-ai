"use client";

import Link from "next/link";

export default function ChatPage() {
  return (
    <div className="flex h-[calc(100vh-64px-1px)] flex-col items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-[var(--color-foreground)]">
          AI Chat — Coming Soon
        </h1>
        <p className="mt-2 text-[var(--color-muted)]">
          Chat feature is temporarily unavailable while we configure the AI provider.
        </p>
        <Link
          href="/"
          className="mt-4 inline-block text-sm font-medium text-[var(--color-primary)] hover:underline"
        >
          Back to Home
        </Link>
      </div>
    </div>
  );
}
