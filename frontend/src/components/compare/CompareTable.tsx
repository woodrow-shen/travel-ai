"use client";

import type { CompareResult } from "@/types";
import { formatPrice } from "@/lib/utils";

interface CompareTableProps {
  results: CompareResult[];
}

export function CompareTable({ results }: CompareTableProps) {
  if (results.length === 0) {
    return (
      <p className="py-8 text-center text-[var(--color-muted)]">
        No comparison data available. Select items to compare.
      </p>
    );
  }

  const allProviders = Array.from(
    new Set(results.flatMap((r) => r.prices.map((p) => p.provider)))
  );

  return (
    <div className="overflow-x-auto">
      <table
        className="w-full border-collapse text-left text-sm"
        role="table"
        aria-label="Price comparison table"
      >
        <thead>
          <tr className="border-b border-[var(--color-border)]">
            <th
              scope="col"
              className="px-4 py-3 font-semibold text-[var(--color-foreground)]"
            >
              Item
            </th>
            {allProviders.map((provider) => (
              <th
                key={provider}
                scope="col"
                className="px-4 py-3 text-center font-semibold text-[var(--color-foreground)]"
              >
                {provider}
              </th>
            ))}
            <th
              scope="col"
              className="px-4 py-3 text-center font-semibold text-[var(--color-foreground)]"
            >
              Best Price
            </th>
          </tr>
        </thead>
        <tbody>
          {results.map((result) => {
            const priceByProvider = new Map(
              result.prices.map((p) => [p.provider, p])
            );

            return (
              <tr
                key={result.item_id}
                className="border-b border-[var(--color-border)] hover:bg-[var(--color-border)]/20"
              >
                <td className="px-4 py-3 font-medium">{result.label}</td>
                {allProviders.map((provider) => {
                  const pricePoint = priceByProvider.get(provider);
                  const isLowest =
                    pricePoint?.price === result.lowest_price;

                  return (
                    <td
                      key={provider}
                      className="px-4 py-3 text-center"
                    >
                      {pricePoint ? (
                        <span
                          className={
                            isLowest
                              ? "font-bold text-[var(--color-success)]"
                              : ""
                          }
                        >
                          {formatPrice(
                            pricePoint.price,
                            pricePoint.currency
                          )}
                        </span>
                      ) : (
                        <span className="text-[var(--color-muted)]">
                          --
                        </span>
                      )}
                    </td>
                  );
                })}
                <td className="px-4 py-3 text-center font-bold text-[var(--color-success)]">
                  {formatPrice(result.lowest_price)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
