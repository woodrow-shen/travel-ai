"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";

export default function ChatPage() {
  const t = useTranslations("chat");

  return (
    <div className="flex h-[calc(100vh-64px-1px)] flex-col items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-[var(--color-foreground)]">
          {t("title")}
        </h1>
        <p className="mt-2 text-[var(--color-muted)]">
          {t("comingSoon")}
        </p>
        <Link
          href="/"
          className="mt-4 inline-block text-sm font-medium text-[var(--color-primary)] hover:underline"
        >
          {t("backToHome")}
        </Link>
      </div>
    </div>
  );
}
