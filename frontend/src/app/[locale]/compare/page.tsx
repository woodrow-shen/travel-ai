"use client";

import { useState, useEffect, useRef } from "react";
import { useTranslations } from "next-intl";
import { useCompare } from "@/hooks/useCompare";
import { useCompareStore } from "@/stores/compare";
import { CompareTable } from "@/components/compare/CompareTable";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import type { SearchType } from "@/types";

export default function ComparePage() {
  const { results, isLoading, error, compare } = useCompare();
  const storeIds = useCompareStore((s) => s.selectedIds);
  const storeType = useCompareStore((s) => s.selectedType);
  const clearSelection = useCompareStore((s) => s.clearSelection);
  const t = useTranslations("compare");
  const tc = useTranslations("common");

  const [itemType, setItemType] = useState<SearchType>("flight");
  const [itemIdsInput, setItemIdsInput] = useState("");
  const autoTriggered = useRef(false);

  useEffect(() => {
    if (storeIds.length >= 2) {
      setItemIdsInput(storeIds.join(", "));
      setItemType(storeType);
    }
  }, [storeIds, storeType]);

  useEffect(() => {
    if (storeIds.length >= 2 && !autoTriggered.current) {
      autoTriggered.current = true;
      compare(storeIds, storeType).then(() => {
        clearSelection();
      });
    }
  }, [storeIds, storeType, compare, clearSelection]);

  const handleCompare = () => {
    const ids = itemIdsInput.split(",").map((id) => id.trim()).filter(Boolean);
    if (ids.length < 2) return;
    compare(ids, itemType);
  };

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-2 text-2xl font-bold">{t("title")}</h1>
      <p className="mb-6 text-[var(--color-muted)]">{t("subtitle")}</p>

      <div className="mb-8 rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
          <div className="flex-1">
            <Input
              label={t("manual.label")}
              placeholder={t("manual.placeholder")}
              value={itemIdsInput}
              onChange={(e) => setItemIdsInput(e.target.value)}
              helperText={t("manual.helperText")}
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="compare-type" className="text-sm font-medium text-[var(--color-foreground)]">
              {tc("type")}
            </label>
            <select
              id="compare-type"
              value={itemType}
              onChange={(e) => setItemType(e.target.value as SearchType)}
              className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] px-3 py-2 text-base focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/30"
            >
              <option value="flight">{t("types.flights")}</option>
              <option value="hotel">{t("types.hotels")}</option>
            </select>
          </div>

          <Button onClick={handleCompare} isLoading={isLoading}>
            {tc("compare")}
          </Button>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded-lg bg-[var(--color-error)]/10 px-4 py-3 text-sm text-[var(--color-error)]" role="alert">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center py-12">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]" aria-label={tc("loading")} />
        </div>
      )}

      {!isLoading && results.length > 0 && (
        <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-6">
          <CompareTable results={results} />
        </div>
      )}
    </div>
  );
}
