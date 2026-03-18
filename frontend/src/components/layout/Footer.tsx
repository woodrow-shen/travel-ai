"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";

export function Footer() {
  const currentYear = new Date().getFullYear();
  const t = useTranslations("footer");

  return (
    <footer className="border-t border-[var(--color-border)] bg-[var(--color-card)]">
      <div className="mx-auto max-w-7xl px-4 py-8">
        <div className="grid gap-8 sm:grid-cols-3">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-muted)]">
              Travel AI
            </h2>
            <p className="mt-2 text-sm text-[var(--color-muted)]">
              {t("description")}
            </p>
          </div>

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-muted)]">
              {t("features")}
            </h2>
            <ul className="mt-2 space-y-1" role="list">
              <li>
                <Link
                  href="/search"
                  className="text-sm text-[var(--color-muted)] hover:text-[var(--color-foreground)]"
                >
                  {t("flightHotelSearch")}
                </Link>
              </li>
              <li>
                <Link
                  href="/compare"
                  className="text-sm text-[var(--color-muted)] hover:text-[var(--color-foreground)]"
                >
                  {t("priceComparison")}
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-muted)]">
              {t("legal")}
            </h2>
            <ul className="mt-2 space-y-1" role="list">
              <li>
                <span className="text-sm text-[var(--color-muted)]">
                  {t("mitLicense")}
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t border-[var(--color-border)] pt-6 text-center">
          <p className="text-sm text-[var(--color-muted)]">
            {t("copyright", { year: String(currentYear) })}
          </p>
        </div>
      </div>
    </footer>
  );
}
