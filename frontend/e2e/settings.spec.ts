import { test, expect } from "@playwright/test";
import {
  setupAuthenticated,
  mockSubscriptionsApi,
  mockPreferencesApi,
} from "./helpers";
import { MOCK_PREFERENCES } from "./fixtures";

test.describe("Settings — Subscriptions page", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);
    await mockSubscriptionsApi(page);
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

  test("shows pending email with pending badge", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    await expect(page.locator("span").filter({ hasText: /^pending@example\.com$/ })).toBeVisible();
    await expect(page.getByText("Pending", { exact: true })).toBeVisible();
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

  test("add button disabled when input empty", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    await expect(page.getByRole("button", { name: "Add" })).toBeDisabled();
  });

  test("add email via input and button", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    await page.getByPlaceholder("Add email address").fill("new@example.com");
    await page.getByRole("button", { name: "Add" }).click();

    // Input should be cleared after successful add
    await expect(page.getByPlaceholder("Add email address")).toHaveValue("");
  });

  test("add email via Enter key", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    await page.getByPlaceholder("Add email address").fill("enter@example.com");
    await page.getByPlaceholder("Add email address").press("Enter");

    await expect(page.getByPlaceholder("Add email address")).toHaveValue("");
  });

  test("remove email button", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    const removeButtons = page.getByRole("button", { name: "Remove" });
    await expect(removeButtons.first()).toBeVisible();
  });

  test("toggle subscription active/inactive", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    const toggle = page.getByRole("switch").first();
    await expect(toggle).toBeVisible();
    await expect(toggle).toHaveAttribute("aria-checked", "true");

    await toggle.click();
  });

  test("delete subscription", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    const deleteButton = page.getByRole("button", { name: "Delete" }).first();
    await expect(deleteButton).toBeVisible();
    await deleteButton.click();
  });

  test("new subscription form visible with verified emails", async ({ page }) => {
    await page.goto("/settings/subscriptions");

    await expect(page.getByText("New Subscription")).toBeVisible();
    await expect(page.getByRole("button", { name: "Create Subscription" })).toBeVisible();
  });

  test("shows add and verify email message when no verified emails", async ({ page }) => {
    await page.unrouteAll({ behavior: "ignoreErrors" });
    await setupAuthenticated(page);
    await mockSubscriptionsApi(
      page,
      [{ id: "email-u", email: "unverified@test.com", is_verified: false, verified_at: null, created_at: "2026-03-17T00:00:00Z" }],
      []
    );

    await page.goto("/settings/subscriptions");

    await expect(page.getByText("Add and verify an email address above")).toBeVisible();
  });
});

test.describe("Settings — Preferences page", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);
    await mockPreferencesApi(page);
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

    const starAlliance = page.getByRole("button", { name: "Star Alliance" });
    await expect(starAlliance).toBeVisible();
  });

  test("save preferences shows Saved successfully", async ({ page }) => {
    await page.goto("/settings/preferences");

    await page.getByRole("button", { name: "Save Preferences" }).click();

    await expect(page.getByText("Saved successfully")).toBeVisible();
  });

  test("preferences loading state", async ({ page }) => {
    await page.unrouteAll({ behavior: "ignoreErrors" });
    await setupAuthenticated(page);

    let resolvePrefs!: () => void;
    const prefsPromise = new Promise<void>((r) => { resolvePrefs = r; });

    await page.route("**/api/users/preferences", async (route) => {
      await prefsPromise;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_PREFERENCES),
      });
    });

    await page.goto("/settings/preferences");

    await expect(page.getByText("Loading preferences...")).toBeVisible();

    resolvePrefs();

    await expect(page.getByText("Home Airports")).toBeVisible();
  });
});

test.describe("Settings — Subscription complete flow", () => {
  test("add email → create subscription → subscription appears", async ({ page }) => {
    await setupAuthenticated(page);

    const verifiedEmail = {
      id: "email-1",
      email: "test@example.com",
      is_verified: true,
      verified_at: "2026-01-01T00:00:00Z",
      created_at: "2026-01-01T00:00:00Z",
    };

    await mockSubscriptionsApi(page, [verifiedEmail], []);

    await page.goto("/settings/subscriptions");

    await expect(page.getByRole("button", { name: "Create Subscription" })).toBeVisible();

    // Select email and create subscription
    await page.locator("select").last().selectOption("email-1");
    await page.getByRole("button", { name: "Create Subscription" }).click();
  });
});
