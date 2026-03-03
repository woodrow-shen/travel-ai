"use client";

import { SearchForm } from "@/components/search/SearchForm";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/Button";

export default function HomePage() {
  const { isAuthenticated, isLoading, login } = useAuth();

  return (
    <div className="flex flex-col">
      {/* Hero section */}
      <section className="bg-gradient-to-b from-[var(--color-primary)]/5 to-transparent px-4 pb-16 pt-20">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="text-4xl font-bold tracking-tight text-[var(--color-foreground)] sm:text-5xl lg:text-6xl">
            Plan Your Perfect Trip with{" "}
            <span className="text-[var(--color-primary)]">AI</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-[var(--color-muted)]">
            Search flights and hotels, compare prices across providers, and let
            our AI assistant help you build the perfect itinerary.
          </p>

          {!isLoading && !isAuthenticated && (
            <div className="mt-8">
              <Button onClick={login} size="lg">
                Sign in with Google
              </Button>
              <p className="mt-3 text-sm text-[var(--color-muted)]">
                Sign in to save trips and access personalized recommendations.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Search section */}
      <section className="px-4 pb-16" aria-label="Search for flights and hotels">
        <div className="mx-auto max-w-4xl">
          <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-card)] p-6 shadow-lg sm:p-8">
            <SearchForm />
          </div>
        </div>
      </section>

      {/* Features section */}
      <section className="px-4 pb-20" aria-label="Features">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-10 text-center text-2xl font-bold text-[var(--color-foreground)]">
            Why Travel AI?
          </h2>
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <div key={feature.title} className="text-center">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold">{feature.title}</h3>
                <p className="mt-2 text-sm text-[var(--color-muted)]">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

const features = [
  {
    title: "Smart Search",
    description:
      "Search flights and hotels across multiple providers in a single query.",
    icon: (
      <svg
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
        />
      </svg>
    ),
  },
  {
    title: "Price Comparison",
    description:
      "Compare prices across providers to find the best deals for your trip.",
    icon: (
      <svg
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z"
        />
      </svg>
    ),
  },
  {
    title: "AI Itinerary",
    description:
      "Chat with our AI to generate day-by-day itineraries tailored to you.",
    icon: (
      <svg
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z"
        />
      </svg>
    ),
  },
];
