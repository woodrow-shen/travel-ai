"use client";

import { useState, useCallback } from "react";
import { api } from "@/lib/api";
import type { CompareResult } from "@/types";

export function useCompare() {
  const [results, setResults] = useState<CompareResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const compare = useCallback(
    async (itemIds: string[], itemType: "flight" | "hotel") => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await api.post<CompareResult[]>("/compare", {
          item_ids: itemIds,
          item_type: itemType,
        });
        setResults(data);
        return data;
      } catch (err: unknown) {
        const message =
          err && typeof err === "object" && "detail" in err
            ? (err as { detail: string }).detail
            : "Comparison failed. Please try again.";
        setError(message);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const clearResults = useCallback(() => {
    setResults([]);
    setError(null);
  }, []);

  return {
    results,
    isLoading,
    error,
    compare,
    clearResults,
  };
}
