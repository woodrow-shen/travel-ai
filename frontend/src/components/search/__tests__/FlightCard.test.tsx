import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { FlightCard } from "../FlightCard";
import type { FlightResult } from "@/types";

const mockFlight: FlightResult = {
  id: "flight-1",
  provider: "amadeus",
  price: 15000,
  currency: "TWD",
  outbound_segments: [
    {
      airline: "China Airlines",
      flight_number: "CI100",
      departure_airport: "TPE",
      arrival_airport: "NRT",
      departure_time: "2026-04-01T08:30:00",
      arrival_time: "2026-04-01T12:30:00",
      duration_minutes: 180,
    },
  ],
  total_duration_minutes: 180,
  stops: 0,
};

const mockRoundtrip: FlightResult = {
  ...mockFlight,
  id: "flight-2",
  return_segments: [
    {
      airline: "China Airlines",
      flight_number: "CI101",
      departure_airport: "NRT",
      arrival_airport: "TPE",
      departure_time: "2026-04-05T14:00:00",
      arrival_time: "2026-04-05T17:00:00",
      duration_minutes: 180,
    },
  ],
};

describe("FlightCard", () => {
  it("renders flight details", () => {
    render(<FlightCard flight={mockFlight} />);
    expect(screen.getByText("China Airlines")).toBeInTheDocument();
    expect(screen.getByText("CI100")).toBeInTheDocument();
    expect(screen.getByText("TPE")).toBeInTheDocument();
    expect(screen.getByText("NRT")).toBeInTheDocument();
    expect(screen.getByText("Direct")).toBeInTheDocument();
    expect(screen.getByText("amadeus")).toBeInTheDocument();
  });

  it("renders departure and arrival times", () => {
    render(<FlightCard flight={mockFlight} />);
    expect(screen.getByText("08:30")).toBeInTheDocument();
    expect(screen.getByText("12:30")).toBeInTheDocument();
  });

  it("shows stop count for non-direct flights", () => {
    const flightWithStops = {
      ...mockFlight,
      stops: 1,
    };
    render(<FlightCard flight={flightWithStops} />);
    expect(screen.getByText("1 stop")).toBeInTheDocument();
  });

  it("shows plural stops", () => {
    const flightWithStops = {
      ...mockFlight,
      stops: 2,
    };
    render(<FlightCard flight={flightWithStops} />);
    expect(screen.getByText("2 stops")).toBeInTheDocument();
  });

  it("calls onSelect when Select button clicked", () => {
    const onSelect = vi.fn();
    render(<FlightCard flight={mockFlight} onSelect={onSelect} />);
    fireEvent.click(screen.getByText("Select"));
    expect(onSelect).toHaveBeenCalledWith(mockFlight);
  });

  it("calls onCompare when Compare button clicked", () => {
    const onCompare = vi.fn();
    render(<FlightCard flight={mockFlight} onCompare={onCompare} />);
    fireEvent.click(screen.getByText("Compare"));
    expect(onCompare).toHaveBeenCalledWith(mockFlight);
  });

  it("hides Select/Compare buttons when callbacks not provided", () => {
    render(<FlightCard flight={mockFlight} />);
    expect(screen.queryByText("Select")).not.toBeInTheDocument();
    expect(screen.queryByText("Compare")).not.toBeInTheDocument();
  });

  it("applies selected ring style", () => {
    render(<FlightCard flight={mockFlight} isSelected />);
    const card = screen.getByRole("article");
    expect(card.className).toContain("ring-2");
  });

  it("renders return leg for roundtrip", () => {
    render(<FlightCard flight={mockRoundtrip} />);
    expect(screen.getByText("Return")).toBeInTheDocument();
    expect(screen.getByText("CI101")).toBeInTheDocument();
    expect(screen.getByText("roundtrip")).toBeInTheDocument();
  });

  it("shows booking link when available", () => {
    const flightWithUrl = {
      ...mockFlight,
      booking_url: "https://example.com/book",
    };
    render(<FlightCard flight={flightWithUrl} />);
    const link = screen.getByText("Book now");
    expect(link).toHaveAttribute("href", "https://example.com/book");
    expect(link).toHaveAttribute("target", "_blank");
  });

  it("has accessible aria-label", () => {
    render(<FlightCard flight={mockFlight} />);
    const card = screen.getByRole("article");
    expect(card).toHaveAttribute(
      "aria-label",
      expect.stringContaining("TPE")
    );
  });
});
