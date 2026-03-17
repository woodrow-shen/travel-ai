import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { Header } from "../Header";

// Mock next/link
vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
    [key: string]: unknown;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

// Mock useAuth hook
const mockLogin = vi.fn();
const mockLogout = vi.fn();
let mockAuthState = {
  user: null as { name: string; picture?: string } | null,
  isAuthenticated: false,
  isLoading: false,
  login: mockLogin,
  logout: mockLogout,
};

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => mockAuthState,
}));

describe("Header", () => {
  beforeEach(() => {
    mockAuthState = {
      user: null,
      isAuthenticated: false,
      isLoading: false,
      login: mockLogin,
      logout: mockLogout,
    };
    vi.clearAllMocks();
  });

  it("renders logo with link to home", () => {
    render(<Header />);
    const logo = screen.getByLabelText("Travel AI - Home");
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute("href", "/");
  });

  it("renders navigation links", () => {
    render(<Header />);
    expect(screen.getAllByText("Search")).toHaveLength(2); // desktop + mobile
    expect(screen.getAllByText("Compare")).toHaveLength(2);
    expect(screen.getAllByText("Trips")).toHaveLength(2);
    expect(screen.getAllByText("Chat")).toHaveLength(2);
  });

  it("shows sign in button when not authenticated", () => {
    render(<Header />);
    const buttons = screen.getAllByText("Sign in with Google");
    expect(buttons.length).toBeGreaterThanOrEqual(1);
  });

  it("calls login when sign in button clicked", () => {
    render(<Header />);
    const buttons = screen.getAllByText("Sign in with Google");
    fireEvent.click(buttons[0]);
    expect(mockLogin).toHaveBeenCalled();
  });

  it("shows loading state", () => {
    mockAuthState = { ...mockAuthState, isLoading: true };
    render(<Header />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("shows user name when authenticated", () => {
    mockAuthState = {
      ...mockAuthState,
      user: { name: "Woodrow", picture: "https://example.com/pic.jpg" },
      isAuthenticated: true,
    };
    render(<Header />);
    expect(screen.getByText("Woodrow")).toBeInTheDocument();
  });

  it("shows sign out button in mobile menu when authenticated", () => {
    mockAuthState = {
      ...mockAuthState,
      user: { name: "Woodrow" },
      isAuthenticated: true,
    };
    render(<Header />);
    expect(screen.getByText("Sign out")).toBeInTheDocument();
  });

  it("shows settings links in mobile menu when authenticated", () => {
    mockAuthState = {
      ...mockAuthState,
      user: { name: "Woodrow" },
      isAuthenticated: true,
    };
    render(<Header />);
    const subLinks = screen.getAllByText("Subscriptions");
    expect(subLinks.length).toBeGreaterThanOrEqual(1);
    const prefLinks = screen.getAllByText("Preferences");
    expect(prefLinks.length).toBeGreaterThanOrEqual(1);
  });

  it("toggles mobile menu", () => {
    render(<Header />);
    const menuButton = screen.getByLabelText("Toggle navigation menu");
    expect(menuButton).toHaveAttribute("aria-expanded", "false");

    fireEvent.click(menuButton);
    expect(menuButton).toHaveAttribute("aria-expanded", "true");

    fireEvent.click(menuButton);
    expect(menuButton).toHaveAttribute("aria-expanded", "false");
  });

  it("marks Chat link as disabled", () => {
    render(<Header />);
    const chatLinks = screen.getAllByText("Chat");
    const disabledChat = chatLinks.find(
      (link) => link.getAttribute("aria-disabled") === "true"
    );
    expect(disabledChat).toBeDefined();
  });
});
