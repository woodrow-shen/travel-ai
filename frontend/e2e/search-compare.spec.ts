import { test, expect } from "@playwright/test";
import { setupAuthenticated } from "./helpers";

const MOCK_FLIGHT_RESULTS = {
  search_id: "search-1",
  type: "flight",
  flights: [
    {
      id: "flight-1",
      provider: "amadeus",
      price: 15000,
      currency: "TWD",
      outbound_segments: [
        {
          airline: "China Airlines",
          flight_number: "CI100",
          departure_airport: "TPE",
          arrival_airport: "NRT",
          departure_time: "2026-04-01T08:30:00",
          arrival_time: "2026-04-01T12:30:00",
          duration_minutes: 180,
          cabin_class: "economy",
        },
      ],
      total_duration_minutes: 180,
      stops: 0,
    },
    {
      id: "flight-2",
      provider: "skyscanner",
      price: 14500,
      currency: "TWD",
      outbound_segments: [
        {
          airline: "EVA Air",
          flight_number: "BR198",
          departure_airport: "TPE",
          arrival_airport: "NRT",
          departure_time: "2026-04-01T10:00:00",
          arrival_time: "2026-04-01T14:00:00",
          duration_minutes: 180,
          cabin_class: "economy",
        },
      ],
      total_duration_minutes: 180,
      stops: 0,
    },
  ],
  hotels: null,
  total_results: 2,
  search_params: {
    type: "flight",
    origin: "TPE",
    destination: "NRT",
    departure_date: "2026-04-01",
    adults: 1,
    currency: "TWD",
  },
  created_at: "2026-04-01T00:00:00Z",
};

const MOCK_COMPARE_RESULTS = [
  {
    item_id: "flight-1",
    item_type: "flight",
    label: "TPE → NRT (CI100)",
    prices: [
      { provider: "amadeus", price: 15000, currency: "TWD", fetched_at: "2026-04-01T00:00:00Z" },
    ],
    lowest_price: 15000,
    highest_price: 15000,
    average_price: 15000,
  },
  {
    item_id: "flight-2",
    item_type: "flight",
    label: "TPE → NRT (BR198)",
    prices: [
      {
        provider: "skyscanner",
        price: 14500,
        currency: "TWD",
        fetched_at: "2026-04-01T00:00:00Z",
      },
    ],
    lowest_price: 14500,
    highest_price: 14500,
    average_price: 14500,
  },
];

test.describe("Search → Results → Compare flow", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);

    await page.route("**/api/search/flights", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_FLIGHT_RESULTS),
      })
    );

    await page.route("**/api/compare/flights", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_COMPARE_RESULTS),
      })
    );
  });

  test("search flights and see results", async ({ page }) => {
    await page.goto("/");

    // Fill in search form
    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");

    // Submit search
    await page.getByRole("button", { name: "Search Flights" }).click();

    // Should navigate to search page with results
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

    // Click Compare on both flights
    const compareButtons = page.getByRole("button", { name: "Compare" });
    await compareButtons.nth(0).click();
    await compareButtons.nth(1).click();

    // Floating compare bar should appear
    await expect(page.getByText("2 selected")).toBeVisible();

    // Click Compare link in floating bar (not the nav link)
    await page.locator(".fixed").getByRole("link", { name: "Compare" }).click();
    await expect(page).toHaveURL("/compare");

    // Compare page loads with heading
    await expect(page.getByRole("heading", { name: "Price Comparison" })).toBeVisible();
  });

  test("sort results by price", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("From").fill("TPE");
    await page.getByRole("textbox", { name: "To" }).fill("NRT");
    await page.getByLabel("Departure").fill("2026-04-01");
    await page.getByRole("button", { name: "Search Flights" }).click();

    await expect(page).toHaveURL("/search");

    // Default sort is price low to high
    await expect(page.getByText("Low to High")).toBeVisible();

    // Toggle sort order
    await page.getByText("Low to High").click();
    await expect(page.getByText("High to Low")).toBeVisible();
  });
});

test.describe("Hotel search flow", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);

    await page.route("**/api/search/hotels", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          search_id: "search-h1",
          type: "hotel",
          flights: null,
          hotels: [
            {
              id: "hotel-1",
              provider: "skyscanner",
              name: "Grand Tokyo Hotel",
              address: "Chiyoda-ku, Tokyo",
              star_rating: 4,
              user_rating: 8.5,
              review_count: 500,
              price_per_night: 5000,
              total_price: 20000,
              currency: "TWD",
              amenities: ["WiFi", "Pool"],
              images: [],
            },
          ],
          total_results: 1,
          search_params: {
            type: "hotel",
            destination: "Tokyo",
            departure_date: "2026-04-01",
            adults: 2,
            currency: "TWD",
            check_in: "2026-04-01",
            check_out: "2026-04-05",
            rooms: 1,
          },
          created_at: "2026-04-01T00:00:00Z",
        }),
      })
    );
  });

  test("search hotels and see results", async ({ page }) => {
    await page.goto("/");

    // Switch to hotel tab
    await page.getByRole("tab", { name: "Hotels" }).click();

    // Fill hotel form
    await page.getByLabel("Destination").fill("Tokyo");
    await page.getByLabel("Check-in").fill("2026-04-01");
    await page.getByLabel("Check-out").fill("2026-04-05");

    await page.getByRole("button", { name: "Search Hotels" }).click();

    await expect(page).toHaveURL("/search");
    await expect(page.getByText("1 result found")).toBeVisible();
    await expect(page.getByText("Grand Tokyo Hotel")).toBeVisible();
  });
});
