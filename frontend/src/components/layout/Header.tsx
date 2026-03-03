"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

export function Header() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navLinks = [
    { href: "/search", label: "Search" },
    { href: "/compare", label: "Compare" },
    { href: "/trip", label: "Trips" },
    { href: "/chat", label: "Chat" },
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
              className="text-sm font-medium text-[var(--color-muted)] transition-colors hover:text-[var(--color-foreground)]"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          {isLoading ? (
            <span className="text-sm text-[var(--color-muted)]">Loading...</span>
          ) : isAuthenticated && user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium">{user.name}</span>
              {user.picture && (
                <img
                  src={user.picture}
                  alt=""
                  className="h-8 w-8 rounded-full"
                  aria-hidden="true"
                />
              )}
              <Button variant="outline" size="sm" onClick={logout}>
                Sign out
              </Button>
            </div>
          ) : (
            <Button onClick={login} size="sm">
              Sign in with Google
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
              className="rounded-md px-3 py-2 text-sm font-medium text-[var(--color-muted)] hover:bg-[var(--color-border)]/30 hover:text-[var(--color-foreground)]"
              onClick={() => setMobileOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <div className="mt-2 border-t border-[var(--color-border)] pt-3">
            {isAuthenticated ? (
              <Button variant="outline" size="sm" onClick={logout} className="w-full">
                Sign out
              </Button>
            ) : (
              <Button onClick={login} size="sm" className="w-full">
                Sign in with Google
              </Button>
            )}
          </div>
        </nav>
      </div>
    </header>
  );
}
