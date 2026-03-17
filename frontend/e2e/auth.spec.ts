import { test, expect } from "@playwright/test";
import { mockGeoCurrency, setupAuthenticated } from "./helpers";

test.describe("Auth flow", () => {
  test("shows sign in button when not authenticated", async ({ page }) => {
    await page.route("**/api/auth/me", (route) =>
      route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "Not authenticated" }) })
    );
    await mockGeoCurrency(page);

    await page.goto("/");

    await expect(
      page.getByRole("button", { name: "Sign in with Google" }).first()
    ).toBeVisible();

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

    await page.getByText("Test User").click();
    await page.getByText("Sign out").first().click();

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

    const nav = page.getByRole("navigation", { name: "Main navigation" });
    await expect(nav.getByText("Search")).toBeVisible();
    await expect(nav.getByText("Compare")).toBeVisible();
    await expect(nav.getByText("Trips")).toBeVisible();
  });
});

test.describe("User menu", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);
    await page.goto("/");
  });

  test("dropdown shows Subscriptions and Preferences links", async ({ page }) => {
    await page.getByText("Test User").click();

    await expect(page.getByRole("link", { name: "Subscriptions" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Preferences" })).toBeVisible();
  });

  test("dropdown closes when clicking outside", async ({ page }) => {
    await page.getByText("Test User").click();
    await expect(page.getByRole("link", { name: "Subscriptions" })).toBeVisible();

    // Click on the page body (outside the dropdown)
    await page.locator("h1").first().click();

    await expect(page.getByRole("link", { name: "Subscriptions" })).not.toBeVisible();
  });

  test("navigates to subscriptions page", async ({ page }) => {
    // Mock subscription endpoints so the page doesn't error
    await page.route("**/api/subscriptions/emails**", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
    );
    await page.route("**/api/subscriptions", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
    );

    await page.getByText("Test User").click();
    await page.getByRole("link", { name: "Subscriptions" }).click();

    await expect(page).toHaveURL("/settings/subscriptions");
    await expect(page.getByText("Subscription Management")).toBeVisible();
  });

  test("navigates to preferences page", async ({ page }) => {
    await page.route("**/api/users/preferences", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ home_airports: [] }) })
    );

    await page.getByText("Test User").click();
    await page.getByRole("link", { name: "Preferences" }).click();

    await expect(page).toHaveURL("/settings/preferences");
    await expect(page.getByRole("heading", { name: "Preferences" })).toBeVisible();
  });
});

test.describe("Mobile menu", () => {
  test("toggle opens and shows navigation links", async ({ page }) => {
    await setupAuthenticated(page);
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto("/");

    // Mobile menu button
    await page.getByLabel("Toggle navigation menu").click();

    const mobileNav = page.getByRole("navigation", { name: "Mobile navigation" });
    await expect(mobileNav.getByText("Search")).toBeVisible();
    await expect(mobileNav.getByText("Compare")).toBeVisible();
    await expect(mobileNav.getByText("Trips")).toBeVisible();
  });

  test("shows settings links when authenticated", async ({ page }) => {
    await setupAuthenticated(page);
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto("/");
    await page.getByLabel("Toggle navigation menu").click();

    const mobileNav = page.getByRole("navigation", { name: "Mobile navigation" });
    await expect(mobileNav.getByText("Subscriptions")).toBeVisible();
    await expect(mobileNav.getByText("Preferences")).toBeVisible();
  });
});
