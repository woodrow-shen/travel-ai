import type { Page } from "@playwright/test";
import {
  MOCK_USER,
  MOCK_FLIGHT_RESULTS,
  MOCK_HOTEL_RESULTS,
  MOCK_COMPARE_RESULTS,
  MOCK_TRIPS,
  MOCK_EMAILS,
  MOCK_SUBSCRIPTIONS,
  MOCK_PREFERENCES,
} from "./fixtures";

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
        ...MOCK_USER,
        tier: opts?.tier ?? "basic",
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

/** Setup as premium user. */
export async function setupAuthenticatedPremium(page: Page) {
  await loginAsTestUser(page);
  await mockAuthMe(page, { tier: "premium" });
  await mockGeoCurrency(page);
}

/** Mock flight search endpoint. */
export async function mockSearchFlights(page: Page, response?: unknown) {
  await page.route("**/api/search/flights", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(response ?? MOCK_FLIGHT_RESULTS),
    })
  );
}

/** Mock hotel search endpoint. */
export async function mockSearchHotels(page: Page, response?: unknown) {
  await page.route("**/api/search/hotels", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(response ?? MOCK_HOTEL_RESULTS),
    })
  );
}

/** Mock compare endpoint (POST /api/compare). */
export async function mockCompareApi(page: Page, response?: unknown) {
  await page.route("**/api/compare", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(response ?? MOCK_COMPARE_RESULTS),
    })
  );
}

/** Mock trips API (GET list, POST create, DELETE). */
export async function mockTripsApi(page: Page, trips?: unknown[]) {
  const tripList = trips ?? MOCK_TRIPS;

  // Match individual trip routes first (more specific)
  await page.route(/\/api\/trips\/[^/]+$/, (route) => {
    if (route.request().method() === "DELETE") {
      return route.fulfill({ status: 204 });
    }
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(tripList[0]),
      });
    }
    return route.fulfill({ status: 405 });
  });

  // Match trips list
  await page.route(/\/api\/trips$/, (route) => {
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(tripList),
      });
    }
    if (route.request().method() === "POST") {
      const body = route.request().postDataJSON();
      return route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          id: "trip-new",
          ...body,
          status: "planning",
          itinerary: [],
          created_at: "2026-03-17T00:00:00Z",
          updated_at: "2026-03-17T00:00:00Z",
        }),
      });
    }
    return route.fulfill({ status: 405 });
  });
}

/** Mock subscriptions API (emails + subscriptions). */
export async function mockSubscriptionsApi(
  page: Page,
  emails?: unknown[],
  subscriptions?: unknown[]
) {
  const emailList = emails ?? MOCK_EMAILS;
  const subList = subscriptions ?? MOCK_SUBSCRIPTIONS;

  // Individual email DELETE — must be registered before the list route
  await page.route(/\/api\/subscriptions\/emails\/[^/]+$/, (route) => {
    if (route.request().method() === "DELETE") {
      return route.fulfill({ status: 204 });
    }
    return route.fulfill({ status: 405 });
  });

  // Email list + create
  await page.route(/\/api\/subscriptions\/emails$/, (route) => {
    const method = route.request().method();
    if (method === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(emailList),
      });
    }
    if (method === "POST") {
      const body = route.request().postDataJSON();
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "email-new",
          email: body.email,
          is_verified: false,
          verified_at: null,
          created_at: "2026-03-17T00:00:00Z",
        }),
      });
    }
    return route.fulfill({ status: 405 });
  });

  // Individual subscription PATCH/DELETE
  await page.route(/\/api\/subscriptions\/(?!emails)[^/]+$/, (route) => {
    const method = route.request().method();
    if (method === "PATCH") {
      const body = route.request().postDataJSON();
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ...(subList[0] as Record<string, unknown>), ...body }),
      });
    }
    if (method === "DELETE") {
      return route.fulfill({ status: 204 });
    }
    return route.fulfill({ status: 405 });
  });

  // Subscription list + create
  await page.route(/\/api\/subscriptions$/, (route) => {
    const method = route.request().method();
    if (method === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(subList),
      });
    }
    if (method === "POST") {
      const body = route.request().postDataJSON();
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "sub-new",
          email_id: body.email_id,
          type: body.type,
          config: body.config ?? {},
          is_active: true,
          last_sent_at: null,
          created_at: "2026-03-17T00:00:00Z",
        }),
      });
    }
    return route.fulfill({ status: 405 });
  });
}

/** Mock preferences API (GET + PATCH). */
export async function mockPreferencesApi(page: Page, preferences?: unknown) {
  const prefs = preferences ?? MOCK_PREFERENCES;

  await page.route("**/api/users/preferences", (route) => {
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(prefs),
      });
    }
    if (route.request().method() === "PATCH") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(route.request().postDataJSON()),
      });
    }
    return route.fulfill({ status: 405 });
  });
}

/** Mock any API endpoint to return an error. */
export async function mockApiError(
  page: Page,
  urlPattern: string | RegExp,
  status: number,
  detail: string
) {
  await page.route(urlPattern, (route) =>
    route.fulfill({
      status,
      contentType: "application/json",
      body: JSON.stringify({ detail }),
    })
  );
}
