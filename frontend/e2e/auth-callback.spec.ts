import { test, expect } from "@playwright/test";
import { mockGeoCurrency } from "./helpers";

test.describe("Auth callback page", () => {
  test.beforeEach(async ({ page }) => {
    // Mock auth/me — won't be called with a valid token until redirect
    await page.route("**/api/auth/me", (route) =>
      route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "Not authenticated" }) })
    );
    await mockGeoCurrency(page);
  });

  test("success with valid access_token", async ({ page }) => {
    await page.goto("/auth/callback?access_token=valid-token&refresh_token=valid-refresh");

    await expect(page.getByText("Successfully signed in")).toBeVisible();
    await expect(page.getByText("Redirecting you to the home page")).toBeVisible();
  });

  test("error param shows authentication failed", async ({ page }) => {
    await page.goto("/auth/callback?error=access_denied");

    await expect(page.getByText("Authentication Failed")).toBeVisible();
    await expect(page.getByText("access_denied")).toBeVisible();
  });

  test("no token shows error message", async ({ page }) => {
    await page.goto("/auth/callback");

    await expect(page.getByText("Authentication Failed")).toBeVisible();
    await expect(page.getByText("No authentication token received.")).toBeVisible();
  });

  test("return to home link works on error", async ({ page }) => {
    await page.goto("/auth/callback?error=server_error");

    await expect(page.getByText("Authentication Failed")).toBeVisible();

    await page.getByText("Return to home").click();
    await expect(page).toHaveURL("/");
  });
});
