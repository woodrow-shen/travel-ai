import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Footer } from "../Footer";

describe("Footer", () => {
  it("renders the brand name", () => {
    render(<Footer />);
    expect(screen.getByText("Travel AI")).toBeInTheDocument();
  });

  it("renders feature links", () => {
    render(<Footer />);
    expect(screen.getByText("Flight & Hotel Search")).toBeInTheDocument();
    expect(screen.getByText("Price Comparison")).toBeInTheDocument();
  });

  it("does not render chat link (disabled)", () => {
    render(<Footer />);
    expect(screen.queryByText("AI Chat Assistant")).not.toBeInTheDocument();
  });

  it("renders MIT license", () => {
    render(<Footer />);
    expect(screen.getByText("MIT License")).toBeInTheDocument();
  });

  it("renders copyright with current year", () => {
    render(<Footer />);
    const year = new Date().getFullYear();
    expect(
      screen.getByText(new RegExp(`${year}`))
    ).toBeInTheDocument();
  });

  it("renders search link with correct href", () => {
    render(<Footer />);
    const searchLink = screen.getByText("Flight & Hotel Search");
    expect(searchLink.closest("a")).toHaveAttribute("href", "/search");
  });
});
