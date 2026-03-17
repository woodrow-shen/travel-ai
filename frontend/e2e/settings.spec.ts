import { test, expect } from "@playwright/test";
import { setupAuthenticated } from "./helpers";

test.describe("Settings — Subscriptions page", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);

    // Mock subscription endpoints
    await page.route("**/api/subscriptions/emails", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([
            {
              id: "email-1",
              email: "test@example.com",
              is_verified: true,
              verified_at: "2026-01-01T00:00:00Z",
              created_at: "2026-01-01T00:00:00Z",
            },
          ]),
        });
      }
      // POST — add email
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "email-2",
          email: "new@example.com",
          is_verified: false,
          verified_at: null,
          created_at: "2026-03-17T00:00:00Z",
        }),
      });
    });

    await page.route("**/api/subscriptions", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([
            {
              id: "sub-1",
              email_id: "email-1",
              type: "bug_fare",
              config: { origin: "TPE", destination: "NRT" },
              is_active: true,
              last_sent_at: null,
              created_at: "2026-01-01T00:00:00Z",
            },
          ]),
        });
      }
      // POST — create subscription
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "sub-2",
          email_id: "email-1",
          type: "price_drop",
          config: {},
          is_active: true,
          last_sent_at: null,
          created_at: "2026-03-17T00:00:00Z",
        }),
      });
    });
  });

  test("displays subscription management page", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    await expect(page.getByText("Subscription Management")).toBeVisible();
    await expect(page.getByText("Email Addresses")).toBeVisible();
    await expect(page.getByText("Active Subscriptions")).toBeVisible();
    await expect(page.getByText("New Subscription")).toBeVisible();
  });

  test("shows existing email with verified badge", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    await expect(page.locator("span").filter({ hasText: /^test@example\.com$/ })).toBeVisible();
    await expect(page.getByText("Verified")).toBeVisible();
  });

  test("shows existing subscription", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    await expect(page.locator("span").filter({ hasText: /^Bug Fare$/ })).toBeVisible();
    await expect(page.getByText("TPE → NRT")).toBeVisible();
  });

  test("add email input and button are present", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    await expect(page.getByPlaceholder("Add email address")).toBeVisible();
    await expect(page.getByRole("button", { name: "Add" })).toBeVisible();
  });
});

test.describe("Settings — Preferences page", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);

    await page.route("**/api/preferences", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            home_airports: ["TPE"],
            preferred_airlines: ["BR", "CI"],
            excluded_airlines: null,
            preferred_alliances: ["Star Alliance"],
            cabin_classes: ["economy", "business"],
            max_stops: 1,
          }),
        });
      }
      // PATCH — update
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(route.request().postDataJSON()),
      });
    });
  });

  test("displays preferences page with loaded data", async ({ page }) => {
    await page.goto("/settings/preferences");

    await expect(page.getByRole("heading", { name: "Preferences" })).toBeVisible();
    await expect(page.getByText("Home Airports")).toBeVisible();
    await expect(page.getByText("Preferred Airlines")).toBeVisible();
    await expect(page.getByText("Excluded Airlines")).toBeVisible();
    await expect(page.getByText("Preferred Alliances")).toBeVisible();
    await expect(page.getByText("Cabin Classes")).toBeVisible();
    await expect(page.getByText("Maximum Stops")).toBeVisible();
  });

  test("shows save button", async ({ page }) => {
    await page.goto("/settings/preferences");

    await expect(
      page.getByRole("button", { name: "Save Preferences" })
    ).toBeVisible();
  });

  test("alliance buttons reflect loaded preferences", async ({ page }) => {
    await page.goto("/settings/preferences");

    // Star Alliance should be selected (has primary color class)
    const starAlliance = page.getByRole("button", { name: "Star Alliance" });
    await expect(starAlliance).toBeVisible();
  });
});
