import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { CompareTable } from "../CompareTable";
import type { CompareResult } from "@/types";

const mockResults: CompareResult[] = [
  {
    item_id: "flight-1",
    item_type: "flight",
    label: "TPE → NRT (CI100)",
    prices: [
      {
        provider: "amadeus",
        price: 15000,
        currency: "TWD",
        fetched_at: "2026-04-01T00:00:00Z",
      },
      {
        provider: "skyscanner",
        price: 14500,
        currency: "TWD",
        fetched_at: "2026-04-01T00:00:00Z",
      },
    ],
    lowest_price: 14500,
    highest_price: 15000,
    average_price: 14750,
  },
  {
    item_id: "flight-2",
    item_type: "flight",
    label: "TPE → NRT (BR198)",
    prices: [
      {
        provider: "amadeus",
        price: 16000,
        currency: "TWD",
        fetched_at: "2026-04-01T00:00:00Z",
      },
    ],
    lowest_price: 16000,
    highest_price: 16000,
    average_price: 16000,
  },
];

describe("CompareTable", () => {
  it("renders empty state when no results", () => {
    render(<CompareTable results={[]} />);
    expect(
      screen.getByText("No comparison data available. Select items to compare.")
    ).toBeInTheDocument();
  });

  it("renders table with correct headers", () => {
    render(<CompareTable results={mockResults} />);
    expect(screen.getByText("Item")).toBeInTheDocument();
    expect(screen.getByText("amadeus")).toBeInTheDocument();
    expect(screen.getByText("skyscanner")).toBeInTheDocument();
    expect(screen.getByText("Best Price")).toBeInTheDocument();
  });

  it("renders item labels", () => {
    render(<CompareTable results={mockResults} />);
    expect(screen.getByText("TPE → NRT (CI100)")).toBeInTheDocument();
    expect(screen.getByText("TPE → NRT (BR198)")).toBeInTheDocument();
  });

  it("shows -- for missing provider prices", () => {
    render(<CompareTable results={mockResults} />);
    // flight-2 only has amadeus, not skyscanner
    const dashes = screen.getAllByText("--");
    expect(dashes.length).toBeGreaterThanOrEqual(1);
  });

  it("has accessible table role and label", () => {
    render(<CompareTable results={mockResults} />);
    const table = screen.getByRole("table");
    expect(table).toHaveAttribute("aria-label", "Price comparison table");
  });

  it("renders provider columns from all results", () => {
    const singleProvider: CompareResult[] = [
      {
        item_id: "f-1",
        item_type: "flight",
        label: "Test Flight",
        prices: [
          {
            provider: "kiwi",
            price: 10000,
            currency: "TWD",
            fetched_at: "2026-04-01T00:00:00Z",
          },
        ],
        lowest_price: 10000,
        highest_price: 10000,
        average_price: 10000,
      },
    ];
    render(<CompareTable results={singleProvider} />);
    expect(screen.getByText("kiwi")).toBeInTheDocument();
    expect(screen.queryByText("amadeus")).not.toBeInTheDocument();
  });
});
