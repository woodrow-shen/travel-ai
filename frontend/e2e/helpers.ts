import type { Page } from "@playwright/test";

/** Inject a fake JWT token into localStorage to simulate an authenticated user. */
export async function loginAsTestUser(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem("access_token", "test-jwt-token");
    localStorage.setItem("refresh_token", "test-refresh-token");
  });
}

/** Mock the /api/auth/me endpoint to return a test user. */
export async function mockAuthMe(page: Page, opts?: { tier?: string }) {
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: "user-1",
        email: "test@example.com",
        name: "Test User",
        picture: null,
        tier: opts?.tier ?? "basic",
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      }),
    })
  );
}

/** Mock the currency detection endpoint. */
export async function mockGeoCurrency(page: Page) {
  await page.route("**/api/geo/currency", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ currency: "TWD" }),
    })
  );
}

/** Standard setup: login + mock auth + mock geo. */
export async function setupAuthenticated(page: Page) {
  await loginAsTestUser(page);
  await mockAuthMe(page);
  await mockGeoCurrency(page);
}
