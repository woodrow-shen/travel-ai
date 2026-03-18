"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/Button";
import { LanguageSwitcher } from "@/components/layout/LanguageSwitcher";
import { cn } from "@/lib/utils";

export function Header() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const t = useTranslations("common");

  const navLinks = [
    { href: "/search" as const, label: t("search") },
    { href: "/compare" as const, label: t("compare") },
    { href: "/trip" as const, label: t("trips") },
    { href: "/monitor" as const, label: t("monitor") },
    { href: "/chat" as const, label: t("chat"), disabled: true },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--color-border)] bg-[var(--color-background)]/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <Link
          href="/"
          className="text-xl font-bold text-[var(--color-primary)]"
          aria-label="Travel AI - Home"
        >
          Travel AI
        </Link>

        {/* Desktop nav */}
        <nav
          className="hidden items-center gap-6 md:flex"
          aria-label="Main navigation"
        >
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "text-sm font-medium transition-colors",
                "disabled" in link && link.disabled
                  ? "text-[var(--color-muted)]/40"
                  : "text-[var(--color-muted)] hover:text-[var(--color-foreground)]"
              )}
              aria-disabled={"disabled" in link && link.disabled ? true : undefined}
              tabIndex={"disabled" in link && link.disabled ? -1 : undefined}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <LanguageSwitcher />
          {isLoading ? (
            <span className="text-sm text-[var(--color-muted)]">{t("loading")}</span>
          ) : isAuthenticated && user ? (
            <UserMenu user={user} onLogout={logout} />
          ) : (
            <Button onClick={login} size="sm">
              {t("signIn")}
            </Button>
          )}
        </div>

        {/* Mobile menu button */}
        <button
          className="inline-flex items-center justify-center rounded-md p-2 md:hidden"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-expanded={mobileOpen}
          aria-controls="mobile-menu"
          aria-label="Toggle navigation menu"
        >
          <svg
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            aria-hidden="true"
          >
            {mobileOpen ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
              />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile menu */}
      <div
        id="mobile-menu"
        className={cn(
          "border-t border-[var(--color-border)] md:hidden",
          mobileOpen ? "block" : "hidden"
        )}
      >
        <nav className="flex flex-col gap-1 px-4 py-3" aria-label="Mobile navigation">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "rounded-md px-3 py-2 text-sm font-medium",
                "disabled" in link && link.disabled
                  ? "text-[var(--color-muted)]/40"
                  : "text-[var(--color-muted)] hover:bg-[var(--color-border)]/30 hover:text-[var(--color-foreground)]"
              )}
              onClick={() => setMobileOpen(false)}
              aria-disabled={"disabled" in link && link.disabled ? true : undefined}
              tabIndex={"disabled" in link && link.disabled ? -1 : undefined}
            >
              {link.label}
            </Link>
          ))}
          {isAuthenticated && (
            <>
              <div className="my-1 border-t border-[var(--color-border)]" />
              <Link
                href="/settings/subscriptions"
                className="rounded-md px-3 py-2 text-sm font-medium text-[var(--color-muted)] hover:bg-[var(--color-border)]/30 hover:text-[var(--color-foreground)]"
                onClick={() => setMobileOpen(false)}
              >
                {t("subscriptions")}
              </Link>
              <Link
                href="/settings/preferences"
                className="rounded-md px-3 py-2 text-sm font-medium text-[var(--color-muted)] hover:bg-[var(--color-border)]/30 hover:text-[var(--color-foreground)]"
                onClick={() => setMobileOpen(false)}
              >
                {t("preferences")}
              </Link>
            </>
          )}
          <div className="my-2 flex items-center gap-2 px-3">
            <LanguageSwitcher />
          </div>
          <div className="mt-2 border-t border-[var(--color-border)] pt-3">
            {isAuthenticated ? (
              <Button variant="outline" size="sm" onClick={logout} className="w-full">
                {t("signOut")}
              </Button>
            ) : (
              <Button onClick={login} size="sm" className="w-full">
                {t("signIn")}
              </Button>
            )}
          </div>
        </nav>
      </div>
    </header>
  );
}

/* ------------------------------------------------------------------ */
/*  User Dropdown Menu                                                 */
/* ------------------------------------------------------------------ */

function UserMenu({
  user,
  onLogout,
}: {
  user: { name: string; picture?: string };
  onLogout: () => void;
}) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const t = useTranslations("common");

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const menuItems = [
    { href: "/settings/subscriptions" as const, label: t("subscriptions") },
    { href: "/settings/preferences" as const, label: t("preferences") },
  ];

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 rounded-lg px-2 py-1.5 transition-colors hover:bg-[var(--color-border)]/30"
        aria-expanded={open}
        aria-haspopup="true"
      >
        {user.picture && (
          <img
            src={user.picture}
            alt=""
            className="h-8 w-8 rounded-full"
            aria-hidden="true"
          />
        )}
        <span className="text-sm font-medium">{user.name}</span>
        <svg
          className={cn("h-4 w-4 text-[var(--color-muted)] transition-transform", open && "rotate-180")}
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2}
          stroke="currentColor"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-48 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] py-1 shadow-lg">
          {menuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block px-4 py-2 text-sm text-[var(--color-foreground)] hover:bg-[var(--color-border)]/30"
              onClick={() => setOpen(false)}
            >
              {item.label}
            </Link>
          ))}
          <div className="my-1 border-t border-[var(--color-border)]" />
          <button
            onClick={() => {
              setOpen(false);
              onLogout();
            }}
            className="block w-full px-4 py-2 text-left text-sm text-[var(--color-error)] hover:bg-[var(--color-border)]/30"
          >
            {t("signOut")}
          </button>
        </div>
      )}
    </div>
  );
}
