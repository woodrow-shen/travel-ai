import { test, expect } from "@playwright/test";
import { setupAuthenticated, mockTripsApi, mockApiError } from "./helpers";
import { MOCK_TRIPS, MOCK_TRIP_WITH_ITINERARY } from "./fixtures";

test.describe("Trip page", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);
  });

  test("empty state", async ({ page }) => {
    await mockTripsApi(page, []);

    await page.goto("/trip");

    await expect(page.getByText("No trips yet.")).toBeVisible();
    await expect(page.getByText("Create your first trip")).toBeVisible();
  });

  test("loading spinner", async ({ page }) => {
    let resolveTrips!: () => void;
    const tripsPromise = new Promise<void>((r) => { resolveTrips = r; });

    await page.route(/\/api\/trips$/, async (route) => {
      await tripsPromise;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_TRIPS),
      });
    });

    await page.goto("/trip");

    await expect(page.getByLabel("Loading trips...")).toBeVisible();

    resolveTrips();

    await expect(page.getByText("Tokyo Spring Trip")).toBeVisible();
  });

  test("trip list with status badges", async ({ page }) => {
    await mockTripsApi(page);

    await page.goto("/trip");

    await expect(page.getByText("Tokyo Spring Trip")).toBeVisible();
    await expect(page.getByText("Osaka Summer")).toBeVisible();
    await expect(page.getByText("Bangkok Weekend")).toBeVisible();

    // Status badges — use exact match to avoid matching other text containing these words
    await expect(page.getByText("planning", { exact: true })).toBeVisible();
    await expect(page.getByText("booked", { exact: true })).toBeVisible();
    await expect(page.getByText("completed", { exact: true })).toBeVisible();
  });

  test("New Trip form toggle (show/cancel)", async ({ page }) => {
    await mockTripsApi(page);

    await page.goto("/trip");

    await page.getByRole("button", { name: "New Trip" }).click();
    await expect(page.getByText("Create New Trip")).toBeVisible();
    await expect(page.getByLabel("Trip Title")).toBeVisible();

    await page.getByRole("button", { name: "Cancel" }).click();
    await expect(page.getByText("Create New Trip")).not.toBeVisible();
  });

  test("create trip successfully", async ({ page }) => {
    await mockTripsApi(page, []);

    await page.goto("/trip");

    await page.getByRole("button", { name: "New Trip" }).click();

    await page.getByLabel("Trip Title").fill("Kyoto Adventure");
    await page.getByLabel("Destination").fill("Kyoto, Japan");
    await page.getByLabel("Start Date").fill("2026-05-01");
    await page.getByLabel("End Date").fill("2026-05-05");

    // Re-mock GET to return the new trip after creation
    await page.unrouteAll({ behavior: "ignoreErrors" });
    await setupAuthenticated(page);

    await page.route(/\/api\/trips$/, (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([{
            id: "trip-new",
            title: "Kyoto Adventure",
            destination: "Kyoto, Japan",
            start_date: "2026-05-01",
            end_date: "2026-05-05",
            status: "planning",
            itinerary: [],
            created_at: "2026-03-17T00:00:00Z",
            updated_at: "2026-03-17T00:00:00Z",
          }]),
        });
      }
      return route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          id: "trip-new",
          title: "Kyoto Adventure",
          destination: "Kyoto, Japan",
          start_date: "2026-05-01",
          end_date: "2026-05-05",
          status: "planning",
          itinerary: [],
          created_at: "2026-03-17T00:00:00Z",
          updated_at: "2026-03-17T00:00:00Z",
        }),
      });
    });

    await page.getByRole("button", { name: "Create Trip" }).click();

    await expect(page.getByText("Create New Trip")).not.toBeVisible();
    await expect(page.getByText("Kyoto Adventure")).toBeVisible();
  });

  test("create trip button does nothing with empty fields", async ({ page }) => {
    await mockTripsApi(page, []);

    await page.goto("/trip");

    await page.getByRole("button", { name: "New Trip" }).click();

    // Only fill title — leave other fields empty
    await page.getByLabel("Trip Title").fill("Incomplete Trip");

    await page.getByRole("button", { name: "Create Trip" }).click();

    // Form should still be visible (not submitted)
    await expect(page.getByText("Create New Trip")).toBeVisible();
  });

  test("delete trip with confirm dialog (accept)", async ({ page }) => {
    await mockTripsApi(page);

    await page.goto("/trip");
    await expect(page.getByText("Tokyo Spring Trip")).toBeVisible();

    page.on("dialog", (dialog) => dialog.accept());

    await page.getByRole("button", { name: "Delete" }).first().click();

    // After delete, the API is re-fetched (mocked to still return trips list)
  });

  test("delete trip cancelled (decline)", async ({ page }) => {
    await mockTripsApi(page);

    await page.goto("/trip");
    await expect(page.getByText("Tokyo Spring Trip")).toBeVisible();

    page.on("dialog", (dialog) => dialog.dismiss());

    await page.getByRole("button", { name: "Delete" }).first().click();

    // Trip should still be visible
    await expect(page.getByText("Tokyo Spring Trip")).toBeVisible();
  });

  test("view trip → itinerary view with Back to trips", async ({ page }) => {
    await mockTripsApi(page, [MOCK_TRIP_WITH_ITINERARY]);

    await page.goto("/trip");
    await expect(page.getByText("Tokyo Adventure")).toBeVisible();

    await page.getByRole("button", { name: "View" }).click();

    await expect(page.getByText("Back to trips")).toBeVisible();
    await expect(page.getByText("Tokyo Adventure")).toBeVisible();
    await expect(page.getByText("Day 1")).toBeVisible();
  });

  test("itinerary empty state", async ({ page }) => {
    const emptyTrip = { ...MOCK_TRIPS[1] }; // Osaka Summer (no itinerary)
    await mockTripsApi(page, [emptyTrip]);

    await page.goto("/trip");
    await page.getByRole("button", { name: "View" }).click();

    await expect(page.getByText("No itinerary items yet.")).toBeVisible();
  });

  test("itinerary shows day-by-day items with type badges", async ({ page }) => {
    await mockTripsApi(page, [MOCK_TRIP_WITH_ITINERARY]);

    await page.goto("/trip");
    await page.getByRole("button", { name: "View" }).click();

    // Day headers
    await expect(page.getByText("Day 1")).toBeVisible();
    await expect(page.getByText("Day 2")).toBeVisible();
    await expect(page.getByText("Day 3")).toBeVisible();

    // Type badges (from typeIcons mapping) — use exact to avoid matching item titles
    await expect(page.getByText("Departure", { exact: true })).toBeVisible(); // flight type
    await expect(page.getByText("Accommodation", { exact: true })).toBeVisible(); // hotel type
    await expect(page.getByText("Activity", { exact: true })).toBeVisible(); // activity type
    await expect(page.getByText("Transfer", { exact: true })).toBeVisible(); // transfer type
    await expect(page.getByText("Note", { exact: true })).toBeVisible(); // note type

    // Item titles
    await expect(page.getByText("Flight to Tokyo")).toBeVisible();
    await expect(page.getByText("Visit Senso-ji Temple")).toBeVisible();
  });

  test("Back to trips returns to list", async ({ page }) => {
    await mockTripsApi(page, [MOCK_TRIP_WITH_ITINERARY]);

    await page.goto("/trip");
    await page.getByRole("button", { name: "View" }).click();

    await expect(page.getByText("Back to trips")).toBeVisible();
    await page.getByText("Back to trips").click();

    await expect(page.getByRole("heading", { name: "My Trips" })).toBeVisible();
  });

  test("error state alert", async ({ page }) => {
    await mockApiError(page, /\/api\/trips$/, 500, "Failed to load trips");

    await page.goto("/trip");

    await expect(page.getByText("Failed to load trips")).toBeVisible();
  });

  test("trip card shows itinerary item count", async ({ page }) => {
    await mockTripsApi(page);

    await page.goto("/trip");

    // First trip has 1 itinerary item
    await expect(page.getByText("1 itinerary item")).toBeVisible();
    // Other trips have 0
    await expect(page.getByText("0 itinerary items").first()).toBeVisible();
  });
});
