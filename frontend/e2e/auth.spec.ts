import { test, expect } from "@playwright/test";
import { mockGeoCurrency, setupAuthenticated } from "./helpers";

test.describe("Auth flow", () => {
  test("shows sign in button when not authenticated", async ({ page }) => {
    // Mock /auth/me to return 401 (no token)
    await page.route("**/api/auth/me", (route) =>
      route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "Not authenticated" }) })
    );
    await mockGeoCurrency(page);

    await page.goto("/");

    await expect(
      page.getByRole("button", { name: "Sign in with Google" }).first()
    ).toBeVisible();

    // Hero section CTA also shows sign in
    await expect(page.getByText("Sign in to save trips")).toBeVisible();
  });

  test("shows user name when authenticated", async ({ page }) => {
    await setupAuthenticated(page);

    await page.goto("/");

    await expect(page.getByText("Test User")).toBeVisible();
  });

  test("logout clears session and returns to home", async ({ page }) => {
    await setupAuthenticated(page);

    await page.goto("/");
    await expect(page.getByText("Test User")).toBeVisible();

    // Open user menu and click sign out
    await page.getByText("Test User").click();
    await page.getByText("Sign out").first().click();

    // Should redirect to home and show sign in
    await expect(page).toHaveURL("/");
  });

  test("unauthenticated user sees sign in on settings pages", async ({ page }) => {
    await page.route("**/api/auth/me", (route) =>
      route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "Not authenticated" }) })
    );
    await mockGeoCurrency(page);

    await page.goto("/settings/subscriptions");
    await expect(page.getByText("Please sign in to manage subscriptions.")).toBeVisible();

    await page.goto("/settings/preferences");
    await expect(page.getByText("Please sign in to manage preferences.")).toBeVisible();
  });

  test("navigation links are visible", async ({ page }) => {
    await setupAuthenticated(page);

    await page.goto("/");

    // Desktop nav
    await expect(page.getByRole("navigation", { name: "Main navigation" }).getByText("Search")).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Main navigation" }).getByText("Compare")).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Main navigation" }).getByText("Trips")).toBeVisible();
  });
});
