"use client";

import { useLocale } from "next-intl";
import { useRouter, usePathname } from "@/i18n/routing";
import { routing } from "@/i18n/routing";

const LOCALE_LABELS: Record<string, string> = {
  "zh-TW": "繁體中文",
  en: "English",
  ja: "日本語",
  ko: "한국어",
  es: "Español",
  fr: "Français",
  de: "Deutsch",
  th: "ไทย",
  vi: "Tiếng Việt",
  "zh-CN": "简体中文",
  "pt-BR": "Português",
  it: "Italiano",
};

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    router.replace(pathname, { locale: e.target.value });
  };

  return (
    <select
      value={locale}
      onChange={handleChange}
      className="rounded-md border border-[var(--color-border)] bg-transparent px-2 py-1 text-sm font-medium text-[var(--color-muted)] outline-none transition-colors hover:text-[var(--color-foreground)] focus:ring-2 focus:ring-[var(--color-primary)]"
      aria-label="Select language"
    >
      {routing.locales.map((loc) => (
        <option key={loc} value={loc}>
          {LOCALE_LABELS[loc] ?? loc}
        </option>
      ))}
    </select>
  );
}
