import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { HotelCard } from "../HotelCard";
import type { HotelResult } from "@/types";

const mockHotel: HotelResult = {
  id: "hotel-1",
  provider: "skyscanner",
  name: "Grand Tokyo Hotel",
  address: "1-1-1 Marunouchi, Chiyoda-ku, Tokyo",
  latitude: 35.6812,
  longitude: 139.7671,
  star_rating: 4,
  user_rating: 8.5,
  review_count: 1234,
  price_per_night: 5000,
  total_price: 20000,
  currency: "TWD",
  amenities: ["WiFi", "Pool", "Gym", "Spa", "Restaurant", "Bar"],
  images: ["https://example.com/hotel1.jpg"],
  booking_url: "https://example.com/book",
  cancellation_policy: "Free cancellation",
};

const mockMinimalHotel: HotelResult = {
  id: "hotel-2",
  provider: "kiwi",
  name: "Budget Inn",
  address: "Somewhere, Tokyo",
  star_rating: 2,
  price_per_night: 1500,
  total_price: 6000,
  currency: "TWD",
  amenities: [],
  images: [],
};

describe("HotelCard", () => {
  it("renders hotel name and address", () => {
    render(<HotelCard hotel={mockHotel} />);
    expect(screen.getByText("Grand Tokyo Hotel")).toBeInTheDocument();
    expect(
      screen.getByText("1-1-1 Marunouchi, Chiyoda-ku, Tokyo")
    ).toBeInTheDocument();
  });

  it("renders star rating", () => {
    render(<HotelCard hotel={mockHotel} />);
    const starContainer = screen.getByLabelText("4 out of 5 stars");
    expect(starContainer).toBeInTheDocument();
  });

  it("renders user rating and review count", () => {
    render(<HotelCard hotel={mockHotel} />);
    expect(screen.getByText("8.5")).toBeInTheDocument();
    expect(screen.getByText("(1,234 reviews)")).toBeInTheDocument();
  });

  it("hides user rating when not provided", () => {
    render(<HotelCard hotel={mockMinimalHotel} />);
    expect(screen.queryByText("reviews)")).not.toBeInTheDocument();
  });

  it("renders price per night and total price", () => {
    render(<HotelCard hotel={mockHotel} />);
    expect(screen.getByText("per night")).toBeInTheDocument();
  });

  it("renders provider name", () => {
    render(<HotelCard hotel={mockHotel} />);
    expect(screen.getByText("skyscanner")).toBeInTheDocument();
  });

  it("renders amenities (max 5 + overflow)", () => {
    render(<HotelCard hotel={mockHotel} />);
    expect(screen.getByText("WiFi")).toBeInTheDocument();
    expect(screen.getByText("Pool")).toBeInTheDocument();
    expect(screen.getByText("Spa")).toBeInTheDocument();
    expect(screen.getByText("+1 more")).toBeInTheDocument();
  });

  it("hides amenities section when empty", () => {
    render(<HotelCard hotel={mockMinimalHotel} />);
    expect(screen.queryByText("WiFi")).not.toBeInTheDocument();
  });

  it("renders hotel image when available", () => {
    render(<HotelCard hotel={mockHotel} />);
    const img = screen.getByAltText("Grand Tokyo Hotel exterior");
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute("src", "https://example.com/hotel1.jpg");
  });

  it("hides image when none available", () => {
    render(<HotelCard hotel={mockMinimalHotel} />);
    expect(
      screen.queryByAltText("Budget Inn exterior")
    ).not.toBeInTheDocument();
  });

  it("renders cancellation policy when available", () => {
    render(<HotelCard hotel={mockHotel} />);
    expect(screen.getByText("Free cancellation")).toBeInTheDocument();
  });

  it("hides cancellation policy when not provided", () => {
    render(<HotelCard hotel={mockMinimalHotel} />);
    expect(screen.queryByText("Free cancellation")).not.toBeInTheDocument();
  });

  it("renders Book now link when booking_url is available", () => {
    render(<HotelCard hotel={mockHotel} />);
    const link = screen.getByText("Book now");
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "https://example.com/book");
    expect(link).toHaveAttribute("target", "_blank");
  });

  it("hides Book now when no booking_url", () => {
    render(<HotelCard hotel={mockMinimalHotel} />);
    expect(screen.queryByText("Book now")).not.toBeInTheDocument();
  });

  it("calls onSelect when Select button clicked", () => {
    const onSelect = vi.fn();
    render(<HotelCard hotel={mockHotel} onSelect={onSelect} />);
    fireEvent.click(screen.getByText("Select"));
    expect(onSelect).toHaveBeenCalledWith(mockHotel);
  });

  it("calls onCompare when Compare button clicked", () => {
    const onCompare = vi.fn();
    render(<HotelCard hotel={mockHotel} onCompare={onCompare} />);
    fireEvent.click(screen.getByText("Compare"));
    expect(onCompare).toHaveBeenCalledWith(mockHotel);
  });

  it("hides Select/Compare buttons when callbacks not provided", () => {
    render(<HotelCard hotel={mockHotel} />);
    expect(screen.queryByText("Select")).not.toBeInTheDocument();
    expect(screen.queryByText("Compare")).not.toBeInTheDocument();
  });

  it("applies selected ring style", () => {
    render(<HotelCard hotel={mockHotel} isSelected />);
    const card = screen.getByRole("article");
    expect(card.className).toContain("ring-2");
  });

  it("has accessible aria-label", () => {
    render(<HotelCard hotel={mockHotel} />);
    const card = screen.getByRole("article");
    expect(card).toHaveAttribute(
      "aria-label",
      expect.stringContaining("Grand Tokyo Hotel")
    );
    expect(card).toHaveAttribute(
      "aria-label",
      expect.stringContaining("4 stars")
    );
  });
});
