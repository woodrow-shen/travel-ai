import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { SearchForm } from "../SearchForm";

// Mock next/navigation
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

// Mock useSearch hook
const mockSearch = vi.fn();
let mockSearchState = {
  searchType: "flight" as "flight" | "hotel",
  setSearchType: vi.fn(),
  search: mockSearch,
  currency: "TWD",
};

vi.mock("@/hooks/useSearch", () => ({
  useSearch: () => mockSearchState,
}));

describe("SearchForm", () => {
  beforeEach(() => {
    mockSearchState = {
      searchType: "flight",
      setSearchType: vi.fn(),
      search: mockSearch,
      currency: "TWD",
    };
    vi.clearAllMocks();
    localStorage.clear();
  });

  it("renders flight/hotel tabs", () => {
    render(<SearchForm />);
    expect(screen.getByRole("tab", { name: "Flights" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Hotels" })).toBeInTheDocument();
  });

  it("shows flight form fields by default", () => {
    render(<SearchForm />);
    expect(screen.getByLabelText("From")).toBeInTheDocument();
    expect(screen.getByLabelText("To")).toBeInTheDocument();
    expect(screen.getByLabelText("Departure")).toBeInTheDocument();
    expect(screen.getByLabelText("Adults")).toBeInTheDocument();
    expect(screen.getByLabelText("Cabin Class")).toBeInTheDocument();
  });

  it("shows roundtrip/one-way sub-tabs in flight mode", () => {
    render(<SearchForm />);
    expect(
      screen.getByRole("tab", { name: "Roundtrip" })
    ).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "One-way" })).toBeInTheDocument();
  });

  it("shows return date field for roundtrip", () => {
    render(<SearchForm />);
    expect(screen.getByLabelText("Return")).toBeInTheDocument();
  });

  it("hides return date for one-way", () => {
    render(<SearchForm />);
    fireEvent.click(screen.getByRole("tab", { name: "One-way" }));
    expect(screen.queryByLabelText("Return")).not.toBeInTheDocument();
  });

  it("shows hotel form when hotel tab is selected", () => {
    mockSearchState = { ...mockSearchState, searchType: "hotel" };
    render(<SearchForm />);
    expect(screen.getByLabelText("Destination")).toBeInTheDocument();
    expect(screen.getByLabelText("Check-in")).toBeInTheDocument();
    expect(screen.getByLabelText("Check-out")).toBeInTheDocument();
    expect(screen.getByLabelText("Guests")).toBeInTheDocument();
    expect(screen.getByLabelText("Rooms")).toBeInTheDocument();
  });

  it("shows Search Hotels button in hotel mode", () => {
    mockSearchState = { ...mockSearchState, searchType: "hotel" };
    render(<SearchForm />);
    expect(
      screen.getByRole("button", { name: "Search Hotels" })
    ).toBeInTheDocument();
  });

  it("shows Search Flights button in flight mode", () => {
    render(<SearchForm />);
    expect(
      screen.getByRole("button", { name: "Search Flights" })
    ).toBeInTheDocument();
  });

  it("calls setSearchType when tab is clicked", () => {
    render(<SearchForm />);
    fireEvent.click(screen.getByRole("tab", { name: "Hotels" }));
    expect(mockSearchState.setSearchType).toHaveBeenCalledWith("hotel");
  });

  it("has search form role", () => {
    render(<SearchForm />);
    expect(screen.getByRole("search")).toBeInTheDocument();
  });

  it("renders cabin class options", () => {
    render(<SearchForm />);
    const select = screen.getByLabelText("Cabin Class");
    expect(select).toBeInTheDocument();
    expect(screen.getByText("Economy")).toBeInTheDocument();
    expect(screen.getByText("Business")).toBeInTheDocument();
    expect(screen.getByText("First Class")).toBeInTheDocument();
  });

  it("renders guest count options in hotel mode", () => {
    mockSearchState = { ...mockSearchState, searchType: "hotel" };
    render(<SearchForm />);
    const guestsSelect = screen.getByLabelText("Guests");
    expect(guestsSelect).toBeInTheDocument();
    const roomsSelect = screen.getByLabelText("Rooms");
    expect(roomsSelect).toBeInTheDocument();
  });
});
