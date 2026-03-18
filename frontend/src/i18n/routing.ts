import { defineRouting } from "next-intl/routing";
import { createNavigation } from "next-intl/navigation";

export const routing = defineRouting({
  locales: ["zh-TW", "en", "ja", "ko", "es", "fr", "de", "th", "vi", "zh-CN", "pt-BR", "it"],
  defaultLocale: "zh-TW",
  localePrefix: "as-needed",
});

export const { Link, redirect, usePathname, useRouter } =
  createNavigation(routing);
