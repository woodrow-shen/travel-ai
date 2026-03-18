import { test, expect } from "@playwright/test";
import {
  setupAuthenticated,
  mockSubscriptionsApi,
  mockPriceHistoryApi,
  mockNotificationsApi,
  mockGeoCurrency,
  loginAsTestUser,
  mockAuthMe,
} from "./helpers";
import { MOCK_SUBSCRIPTIONS, MOCK_NOTIFICATIONS } from "./fixtures";

test.describe("Monitor — Unauthenticated", () => {
  test("shows sign-in required message", async ({ page }) => {
    // No auth setup — mock /auth/me to return 401
    await page.route("**/api/auth/me", (route) =>
      route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "Unauthorized" }) })
    );
    await mockGeoCurrency(page);

    await page.goto("/monitor");

    await expect(page.getByText("Please sign in to view price monitoring")).toBeVisible();
  });
});

test.describe("Monitor — Authenticated, no subscriptions", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);
    await mockSubscriptionsApi(page, [], []);
    await mockNotificationsApi(page, []);
    await mockPriceHistoryApi(page);
  });

  test("shows page title and empty states", async ({ page }) => {
    await page.goto("/monitor");

    await expect(page.getByRole("heading", { name: "Price Monitoring" })).toBeVisible();
    await expect(page.getByText("No subscriptions yet")).toBeVisible();
    await expect(page.getByText("No notifications sent yet")).toBeVisible();
  });

  test("route selector has no options", async ({ page }) => {
    await page.goto("/monitor");

    const select = page.locator("#route-selector");
    await expect(select).toBeVisible();

    // Only the placeholder option
    const options = select.locator("option");
    await expect(options).toHaveCount(1);
    await expect(options.first()).toHaveText("Select a route...");
  });
});

test.describe("Monitor — Authenticated, with subscriptions", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);
    await mockSubscriptionsApi(page);
    await mockNotificationsApi(page);
    await mockPriceHistoryApi(page);
  });

  test("displays subscription cards", async ({ page }) => {
    await page.goto("/monitor");

    // Check subscription card text (not <option> elements)
    await expect(page.locator("p.font-semibold", { hasText: "TPE → NRT" })).toBeVisible();
    await expect(page.locator("p.font-semibold", { hasText: "TPE → KIX" })).toBeVisible();
  });

  test("route selector shows subscribed routes", async ({ page }) => {
    await page.goto("/monitor");

    const select = page.locator("#route-selector");
    const options = select.locator("option");
    // placeholder + 2 routes
    await expect(options).toHaveCount(3);
    await expect(options.nth(1)).toHaveText("TPE → NRT");
    await expect(options.nth(2)).toHaveText("TPE → KIX");
  });

  test("selecting a route shows price trend chart section", async ({ page }) => {
    await page.goto("/monitor");

    // Chart section should not be visible before selection
    await expect(page.getByText("Price Trend")).not.toBeVisible();

    // Select a route
    await page.locator("#route-selector").selectOption("TPE-NRT");

    // Chart section appears
    await expect(page.getByText("Price Trend")).toBeVisible();
  });

  test("chart shows no-data message when API returns empty points", async ({ page }) => {
    // Override price history with empty response
    await page.unrouteAll({ behavior: "ignoreErrors" });
    await setupAuthenticated(page);
    await mockNotificationsApi(page);
    await mockSubscriptionsApi(page);
    await mockPriceHistoryApi(page, { origin: "TPE", destination: "NRT", days: 30, points: [] });

    await page.goto("/monitor");

    await page.locator("#route-selector").selectOption("TPE-NRT");

    await expect(
      page.getByText("No price data available")
    ).toBeVisible();
  });

  test("notification history displays entries with status badges", async ({ page }) => {
    await page.goto("/monitor");

    // Check notification subjects
    await expect(page.getByText("Bug Fare Alert: TPE → NRT")).toBeVisible();
    await expect(page.getByText("Price Drop: TPE → NRT")).toBeVisible();

    // Check status badges
    await expect(page.getByText("Sent", { exact: true })).toBeVisible();
    await expect(page.getByText("Failed", { exact: true })).toBeVisible();
  });

  test("day toggle buttons are present and switch", async ({ page }) => {
    await page.goto("/monitor");

    const btn30 = page.getByRole("button", { name: "30d" });
    const btn90 = page.getByRole("button", { name: "90d" });

    await expect(btn30).toBeVisible();
    await expect(btn90).toBeVisible();

    // 30d is default (has primary bg)
    await expect(btn30).toHaveClass(/bg-\[var\(--color-primary\)\]/);

    // Click 90d
    await btn90.click();
    await expect(btn90).toHaveClass(/bg-\[var\(--color-primary\)\]/);
  });

  test("subscription toggle button is present", async ({ page }) => {
    await page.goto("/monitor");

    const toggles = page.getByRole("button", { name: "Toggle subscription" });
    await expect(toggles).toHaveCount(2);
  });

  test("clicking subscription card selects route", async ({ page }) => {
    await page.goto("/monitor");

    // Click on the TPE → NRT subscription card (not the <option> element)
    await page.locator("p.font-semibold", { hasText: "TPE → NRT" }).click();

    // Route selector should now have TPE-NRT selected
    await expect(page.locator("#route-selector")).toHaveValue("TPE-NRT");

    // Chart section should appear
    await expect(page.getByText("Price Trend")).toBeVisible();
  });
});

test.describe("Monitor — Navigation", () => {
  test("Monitor link is present in header nav", async ({ page }) => {
    await setupAuthenticated(page);
    await mockSubscriptionsApi(page, [], []);
    await mockNotificationsApi(page, []);

    await page.goto("/");

    const monitorLink = page.getByRole("link", { name: "Monitor" });
    await expect(monitorLink).toBeVisible();

    await monitorLink.click();
    await page.waitForURL("**/monitor");

    await expect(page.getByRole("heading", { name: "Price Monitoring" })).toBeVisible();
  });
});

test.describe("Monitor — Language switch", () => {
  test("page translates to Traditional Chinese", async ({ page }) => {
    await loginAsTestUser(page);
    await mockAuthMe(page);
    await mockGeoCurrency(page);
    await mockNotificationsApi(page, []);
    await mockSubscriptionsApi(page, [], []);

    await page.goto("/zh-TW/monitor");

    // zh-TW translations
    await expect(page.getByRole("heading", { name: "價格監控" })).toBeVisible();
    await expect(page.getByText("尚無訂閱，請至設定中建立。")).toBeVisible();
    await expect(page.getByText("尚無通知紀錄。")).toBeVisible();
  });
});
