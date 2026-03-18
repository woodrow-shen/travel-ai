"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { usePreferences } from "@/hooks/usePreferences";
import { Button } from "@/components/ui/Button";
import { LanguageSwitcher } from "@/components/layout/LanguageSwitcher";

const ALLIANCES = ["Star Alliance", "oneworld", "SkyTeam"];

export default function PreferencesPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const t = useTranslations("settings.preferences");
  const tc = useTranslations("common");

  if (authLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <p className="text-[var(--color-muted)]">{tc("loading")}</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <p className="text-[var(--color-muted)]">{t("signInRequired")}</p>
      </div>
    );
  }

  return <PreferencesContent />;
}

function PreferencesContent() {
  const { preferences, isLoading, isSaving, error, updatePreferences } = usePreferences();
  const t = useTranslations("settings.preferences");

  const [homeAirports, setHomeAirports] = useState("");
  const [preferredAirlines, setPreferredAirlines] = useState("");
  const [excludedAirlines, setExcludedAirlines] = useState("");
  const [alliances, setAlliances] = useState<string[]>([]);
  const [cabinClasses, setCabinClasses] = useState<string[]>([]);
  const [maxStops, setMaxStops] = useState("");
  const [saved, setSaved] = useState(false);

  const cabinClassOptions = [
    { value: "economy", label: t("cabinClasses.economy") || "Economy" },
    { value: "premium_economy", label: t("cabinClasses.premiumEconomy") || "Premium Economy" },
    { value: "business", label: t("cabinClasses.business") || "Business" },
    { value: "first", label: t("cabinClasses.first") || "First" },
  ];

  const maxStopsOptions = [
    { value: "", label: t("maxStops.any") },
    { value: "0", label: t("maxStops.nonStop") },
    { value: "1", label: t("maxStops.max1") },
    { value: "2", label: t("maxStops.max2") },
  ];

  useEffect(() => {
    if (preferences) {
      setHomeAirports(preferences.home_airports?.join(", ") ?? "");
      setPreferredAirlines(preferences.preferred_airlines?.join(", ") ?? "");
      setExcludedAirlines(preferences.excluded_airlines?.join(", ") ?? "");
      setAlliances(preferences.preferred_alliances ?? []);
      setCabinClasses(preferences.cabin_classes ?? []);
      setMaxStops(preferences.max_stops?.toString() ?? "");
    }
  }, [preferences]);

  const parseList = (value: string): string[] | null => {
    const items = value.split(",").map((s) => s.trim().toUpperCase()).filter(Boolean);
    return items.length > 0 ? items : null;
  };

  const handleSave = async () => {
    setSaved(false);
    try {
      await updatePreferences({
        home_airports: parseList(homeAirports),
        preferred_airlines: parseList(preferredAirlines),
        excluded_airlines: parseList(excludedAirlines),
        preferred_alliances: alliances.length > 0 ? alliances : null,
        cabin_classes: cabinClasses.length > 0 ? cabinClasses : null,
        max_stops: maxStops ? parseInt(maxStops, 10) : null,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      // error is set in store
    }
  };

  const toggleItem = (list: string[], item: string, setter: (v: string[]) => void) => {
    setter(list.includes(item) ? list.filter((i) => i !== item) : [...list, item]);
  };

  if (isLoading) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="mb-8 text-2xl font-bold">{t("title")}</h1>
        <p className="text-sm text-[var(--color-muted)]">{t("loading")}</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="mb-8 text-2xl font-bold">{t("title")}</h1>

      {error && (
        <div className="mb-6 rounded-lg border border-[var(--color-error)]/30 bg-[var(--color-error)]/10 px-4 py-3 text-sm text-[var(--color-error)]">
          {error}
        </div>
      )}

      <div className="space-y-6">
        {/* Language */}
        <FieldGroup label={t("language.label")}>
          <LanguageSwitcher />
        </FieldGroup>

        {/* Home Airports */}
        <FieldGroup label={t("homeAirports.label")} hint={t("homeAirports.hint")}>
          <input
            type="text"
            value={homeAirports}
            onChange={(e) => setHomeAirports(e.target.value)}
            placeholder="TPE, TSA"
            className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm uppercase outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
        </FieldGroup>

        {/* Preferred Airlines */}
        <FieldGroup label={t("preferredAirlines.label")} hint={t("preferredAirlines.hint")}>
          <input
            type="text"
            value={preferredAirlines}
            onChange={(e) => setPreferredAirlines(e.target.value)}
            placeholder="BR, CI, NH"
            className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm uppercase outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
        </FieldGroup>

        {/* Excluded Airlines */}
        <FieldGroup label={t("excludedAirlines.label")} hint={t("excludedAirlines.hint")}>
          <input
            type="text"
            value={excludedAirlines}
            onChange={(e) => setExcludedAirlines(e.target.value)}
            placeholder="TR, MM"
            className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm uppercase outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
        </FieldGroup>

        {/* Alliances */}
        <FieldGroup label={t("alliances.label")}>
          <div className="flex flex-wrap gap-2">
            {ALLIANCES.map((a) => (
              <button
                key={a}
                type="button"
                onClick={() => toggleItem(alliances, a, setAlliances)}
                className={`rounded-full border px-3 py-1.5 text-sm transition-colors ${
                  alliances.includes(a)
                    ? "border-[var(--color-primary)] bg-[var(--color-primary)]/10 text-[var(--color-primary)]"
                    : "border-[var(--color-border)] text-[var(--color-muted)] hover:border-[var(--color-primary)]/50"
                }`}
              >
                {a}
              </button>
            ))}
          </div>
        </FieldGroup>

        {/* Cabin Classes */}
        <FieldGroup label={t("cabinClasses.label")}>
          <div className="flex flex-wrap gap-2">
            {cabinClassOptions.map((c) => (
              <button
                key={c.value}
                type="button"
                onClick={() => toggleItem(cabinClasses, c.value, setCabinClasses)}
                className={`rounded-full border px-3 py-1.5 text-sm transition-colors ${
                  cabinClasses.includes(c.value)
                    ? "border-[var(--color-primary)] bg-[var(--color-primary)]/10 text-[var(--color-primary)]"
                    : "border-[var(--color-border)] text-[var(--color-muted)] hover:border-[var(--color-primary)]/50"
                }`}
              >
                {c.label}
              </button>
            ))}
          </div>
        </FieldGroup>

        {/* Max Stops */}
        <FieldGroup label={t("maxStops.label")}>
          <select
            value={maxStops}
            onChange={(e) => setMaxStops(e.target.value)}
            className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            {maxStopsOptions.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </FieldGroup>

        {/* Save */}
        <div className="flex items-center gap-3">
          <Button onClick={handleSave} isLoading={isSaving}>
            {t("saveButton")}
          </Button>
          {saved && (
            <span className="text-sm text-green-600">{t("saved")}</span>
          )}
        </div>
      </div>
    </main>
  );
}

function FieldGroup({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium">{label}</label>
      {hint && <p className="mb-2 text-xs text-[var(--color-muted)]">{hint}</p>}
      {children}
    </div>
  );
}
