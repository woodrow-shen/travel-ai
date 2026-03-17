import { test, expect } from "@playwright/test";
import {
  setupAuthenticated,
  mockSearchFlights,
  mockSearchHotels,
  mockCompareApi,
  mockApiError,
} from "./helpers";
import {
  MOCK_FLIGHT_RESULTS,
  MOCK_FLIGHT_RESULTS_EMPTY,
  MOCK_ROUNDTRIP_FLIGHT_RESULTS,
  MOCK_HOTEL_RESULTS,
  MOCK_HOTEL_COMPARE_RESULTS,
} from "./fixtures";

test.describe("Search → Results → Compare flow", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);
    await mockSearchFlights(page);
    await mockCompareApi(page);
  });

  test("search flights and see results", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");

    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");
    await expect(page.getByText("2 results found")).toBeVisible();
    await expect(page.getByText("China Airlines")).toBeVisible();
    await expect(page.getByText("EVA Air")).toBeVisible();
  });

  test("select flights and navigate to compare", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");

    const compareButtons = page.getByRole("button", { name: "Compare" });
    await compareButtons.nth(0).click();
    await compareButtons.nth(1).click();

    await expect(page.getByText("2 selected")).toBeVisible();

    await page.locator(".fixed").getByRole("link", { name: "Compare" }).click();
    await expect(page).toHaveURL("/compare");

    await expect(page.getByRole("heading", { name: "Price Comparison" })).toBeVisible();
  });

  test("sort results by price", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");
    await expect(page.getByText("Low to High")).toBeVisible();

    await page.getByText("Low to High").click();
    await expect(page.getByText("High to Low")).toBeVisible();
  });

  test("sort by duration", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");

    await page.locator("#sort-by").selectOption("duration");
    await expect(page.locator("#sort-by")).toHaveValue("duration");
  });

  test("sort toggle ascending and descending", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");

    await expect(page.getByText("Low to High")).toBeVisible();
    await page.getByText("Low to High").click();
    await expect(page.getByText("High to Low")).toBeVisible();
    await page.getByText("High to Low").click();
    await expect(page.getByText("Low to High")).toBeVisible();
  });

  test("loading spinner during search", async ({ page }) => {
    await page.unrouteAll({ behavior: "ignoreErrors" });
    await setupAuthenticated(page);

    let resolveFlight!: () => void;
    const flightPromise = new Promise<void>((r) => { resolveFlight = r; });

    await page.route("**/api/search/flights", async (route) => {
      await flightPromise;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_FLIGHT_RESULTS),
      });
    });

    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page.getByRole("button", { name: "Searching Flights..." })).toBeVisible();

    resolveFlight();

    await expect(page).toHaveURL("/search");
    await expect(page.getByText("2 results found")).toBeVisible();
  });

  test("error state on API 500", async ({ page }) => {
    await page.unrouteAll({ behavior: "ignoreErrors" });
    await setupAuthenticated(page);
    await mockApiError(page, "**/api/search/flights", 500, "Internal server error");

    await page.goto("/search");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page.getByText("Internal server error")).toBeVisible();
  });

  test("empty results message", async ({ page }) => {
    await page.unrouteAll({ behavior: "ignoreErrors" });
    await setupAuthenticated(page);
    await mockSearchFlights(page, MOCK_FLIGHT_RESULTS_EMPTY);

    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");
    await expect(page.getByText("No results found")).toBeVisible();
  });

  test("compare bar appears with 2+ items selected", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");

    const compareButtons = page.getByRole("button", { name: "Compare" });

    // Select 1 — no bar
    await compareButtons.nth(0).click();
    await expect(page.getByText("selected")).not.toBeVisible();

    // Select 2 — bar visible
    await compareButtons.nth(1).click();
    await expect(page.getByText("2 selected")).toBeVisible();
  });

  test("compare bar Clear button deselects all", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");

    const compareButtons = page.getByRole("button", { name: "Compare" });
    await compareButtons.nth(0).click();
    await compareButtons.nth(1).click();
    await expect(page.getByText("2 selected")).toBeVisible();

    await page.getByLabel("Clear selection").click();
    await expect(page.getByText("selected")).not.toBeVisible();
  });

  test("flight card displays correct details", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");

    // Default sort is price asc — EVA Air (14500) comes first
    const firstCard = page.locator("[role=article]").first();
    await expect(firstCard.getByText("EVA Air")).toBeVisible();
    await expect(firstCard.getByText("BR198")).toBeVisible();
    await expect(firstCard.getByText("TPE").first()).toBeVisible();
    await expect(firstCard.getByText("NRT").first()).toBeVisible();
    await expect(firstCard.getByText("Direct")).toBeVisible();
    await expect(firstCard.getByText("skyscanner")).toBeVisible();
  });
});

test.describe("One-way flight search", () => {
  test("one-way search complete flow", async ({ page }) => {
    await setupAuthenticated(page);
    await mockSearchFlights(page);

    await page.goto("/");

    await page.getByRole("tab", { name: "One-way" }).click();

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");

    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");
    await expect(page.getByText("2 results found")).toBeVisible();
  });

  test("return date hidden for one-way, visible for roundtrip", async ({ page }) => {
    await setupAuthenticated(page);

    await page.goto("/");

    // Default is roundtrip — Return field visible
    await expect(page.getByLabel("Return")).toBeVisible();

    // Switch to one-way
    await page.getByRole("tab", { name: "One-way" }).click();
    await expect(page.getByLabel("Return")).not.toBeVisible();

    // Back to roundtrip
    await page.getByRole("tab", { name: "Roundtrip" }).click();
    await expect(page.getByLabel("Return")).toBeVisible();
  });
});

test.describe("Roundtrip flight search", () => {
  test("roundtrip search complete flow", async ({ page }) => {
    await setupAuthenticated(page);
    await mockSearchFlights(page, MOCK_ROUNDTRIP_FLIGHT_RESULTS);

    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByLabel("Return").fill("2026-04-08");

    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");
    await expect(page.getByText("1 result found")).toBeVisible();
    // Return label in the card
    await expect(page.getByText("Return", { exact: true }).first()).toBeVisible();
  });
});

test.describe("Tab switching", () => {
  test("switching between flights and hotels tabs", async ({ page }) => {
    await setupAuthenticated(page);

    await page.goto("/");

    // Default tab is flights
    await expect(page.getByLabel("From")).toBeVisible();

    // Switch to hotels
    await page.getByRole("tab", { name: "Hotels" }).click();
    await expect(page.getByLabel("Destination")).toBeVisible();
    await expect(page.getByLabel("Check-in")).toBeVisible();
    await expect(page.getByLabel("Check-out")).toBeVisible();

    // Switch back to flights
    await page.getByRole("tab", { name: "Flights" }).click();
    await expect(page.getByLabel("From")).toBeVisible();
  });
});

test.describe("Hotel search flow", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);
    await mockSearchHotels(page);
  });

  test("search hotels and see results", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("tab", { name: "Hotels" }).click();

    await page.getByLabel("Destination").fill("Tokyo");
    await page.getByLabel("Check-in").fill("2026-04-01");
    await page.getByLabel("Check-out").fill("2026-04-05");

    await page.getByRole("button", { name: "Search Hotels" }).click();

    await expect(page).toHaveURL("/search");
    await expect(page.getByText("2 results found")).toBeVisible();
    await expect(page.getByText("Grand Tokyo Hotel")).toBeVisible();
    await expect(page.getByText("Shinjuku Inn")).toBeVisible();
  });

  test("hotel card displays stars, amenities, and price label", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("tab", { name: "Hotels" }).click();

    await page.getByLabel("Destination").fill("Tokyo");
    await page.getByLabel("Check-in").fill("2026-04-01");
    await page.getByLabel("Check-out").fill("2026-04-05");
    await page.getByRole("button", { name: "Search Hotels" }).click();

    await expect(page).toHaveURL("/search");

    // Default sort is price asc — Shinjuku Inn (3000) comes first
    const firstCard = page.locator("[role=article]").first();
    await expect(firstCard.getByText("Shinjuku Inn")).toBeVisible();
    await expect(firstCard.getByLabel("3 out of 5 stars")).toBeVisible();
    await expect(firstCard.getByText("WiFi")).toBeVisible();
    await expect(firstCard.getByText("per night")).toBeVisible();

    // Second card — Grand Tokyo Hotel
    const secondCard = page.locator("[role=article]").nth(1);
    await expect(secondCard.getByText("Grand Tokyo Hotel")).toBeVisible();
    await expect(secondCard.getByLabel("4 out of 5 stars")).toBeVisible();
    await expect(secondCard.getByText("Pool")).toBeVisible();
  });

  test("hotel search → select → compare flow", async ({ page }) => {
    await mockCompareApi(page, MOCK_HOTEL_COMPARE_RESULTS);

    await page.goto("/");

    await page.getByRole("tab", { name: "Hotels" }).click();

    await page.getByLabel("Destination").fill("Tokyo");
    await page.getByLabel("Check-in").fill("2026-04-01");
    await page.getByLabel("Check-out").fill("2026-04-05");
    await page.getByRole("button", { name: "Search Hotels" }).click();

    await expect(page).toHaveURL("/search");

    const compareButtons = page.getByRole("button", { name: "Compare" });
    await compareButtons.nth(0).click();
    await compareButtons.nth(1).click();
    await expect(page.getByText("2 selected")).toBeVisible();

    await page.locator(".fixed").getByRole("link", { name: "Compare" }).click();
    await expect(page).toHaveURL("/compare");
    await expect(page.getByRole("heading", { name: "Price Comparison" })).toBeVisible();
  });
});
