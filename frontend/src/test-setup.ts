import "@testing-library/jest-dom/vitest";
import React from "react";
import { vi } from "vitest";
import messages from "../messages/en.json";

// Resolve nested key from messages object
function resolveKey(
  obj: Record<string, unknown>,
  key: string,
): unknown {
  const parts = key.split(".");
  let current: unknown = obj;
  for (const part of parts) {
    if (current && typeof current === "object" && part in current) {
      current = (current as Record<string, unknown>)[part];
    } else {
      return undefined;
    }
  }
  return current;
}

// Mock next-intl — returns real English translations
vi.mock("next-intl", () => ({
  useTranslations: (namespace?: string) => {
    const base = namespace
      ? resolveKey(
          messages as Record<string, unknown>,
          namespace,
        )
      : messages;
    const section =
      base && typeof base === "object"
        ? (base as Record<string, unknown>)
        : (messages as Record<string, unknown>);

    const t = (key: string, params?: Record<string, unknown>) => {
      const raw = resolveKey(section, key);
      let result = typeof raw === "string" ? raw : key;
      if (params) {
        for (const [k, v] of Object.entries(params)) {
          result = result.replace(`{${k}}`, String(v));
        }
        // Handle ICU plural: {count, plural, one {} other {s}}
        result = result.replace(
          /\{(\w+), plural, one \{([^}]*)\} other \{([^}]*)\}\}/g,
          (_match, paramName, _one, other) => {
            const val = params[paramName];
            return Number(val) === 1 ? "" : other;
          },
        );
      }
      return result;
    };
    t.rich = (
      key: string,
      params?: Record<string, unknown>,
    ) => {
      const raw = resolveKey(section, key);
      let result: unknown =
        typeof raw === "string" ? raw : key;
      if (params) {
        for (const [k, v] of Object.entries(params)) {
          if (typeof v === "function") {
            result = v(result);
          } else {
            result = String(result).replace(
              `{${k}}`,
              String(v),
            );
          }
        }
      }
      return result;
    };
    return t;
  },
  useLocale: () => "en",
  NextIntlClientProvider: ({
    children,
  }: {
    children: React.ReactNode;
  }) => children,
}));

// Mock @/i18n/routing
vi.mock("@/i18n/routing", () => ({
  Link: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
    [key: string]: unknown;
  }) => React.createElement("a", { href, ...props }, children),
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => "/",
  redirect: vi.fn(),
  routing: {
    locales: ["zh-TW", "en"],
    defaultLocale: "zh-TW",
  },
}));
