import Link from "next/link";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-[var(--color-border)] bg-[var(--color-card)]">
      <div className="mx-auto max-w-7xl px-4 py-8">
        <div className="grid gap-8 sm:grid-cols-3">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-muted)]">
              Travel AI
            </h2>
            <p className="mt-2 text-sm text-[var(--color-muted)]">
              AI-powered travel planning and price comparison.
            </p>
          </div>

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-muted)]">
              Features
            </h2>
            <ul className="mt-2 space-y-1" role="list">
              <li>
                <Link
                  href="/search"
                  className="text-sm text-[var(--color-muted)] hover:text-[var(--color-foreground)]"
                >
                  Flight & Hotel Search
                </Link>
              </li>
              <li>
                <Link
                  href="/compare"
                  className="text-sm text-[var(--color-muted)] hover:text-[var(--color-foreground)]"
                >
                  Price Comparison
                </Link>
              </li>
              <li>
                <Link
                  href="/chat"
                  className="text-sm text-[var(--color-muted)] hover:text-[var(--color-foreground)]"
                >
                  AI Chat Assistant
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-muted)]">
              Legal
            </h2>
            <ul className="mt-2 space-y-1" role="list">
              <li>
                <span className="text-sm text-[var(--color-muted)]">
                  MIT License
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t border-[var(--color-border)] pt-6 text-center">
          <p className="text-sm text-[var(--color-muted)]">
            &copy; {currentYear} Woodrow Shen. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
