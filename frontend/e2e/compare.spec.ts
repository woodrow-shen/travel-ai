import { test, expect } from "@playwright/test";
import { setupAuthenticated, mockCompareApi, mockApiError } from "./helpers";
import { MOCK_COMPARE_RESULTS, MOCK_HOTEL_COMPARE_RESULTS } from "./fixtures";

test.describe("Compare page", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);
  });

  test("page heading and description", async ({ page }) => {
    await page.goto("/compare");

    await expect(page.getByRole("heading", { name: "Price Comparison" })).toBeVisible();
    await expect(page.getByText("Compare prices across different providers")).toBeVisible();
  });

  test("manual ID input, type selector, and Compare button", async ({ page }) => {
    await page.goto("/compare");

    await expect(page.getByLabel("Item IDs (comma separated)")).toBeVisible();
    await expect(page.getByLabel("Type")).toBeVisible();
    await expect(page.getByRole("button", { name: "Compare" })).toBeVisible();
  });

  test("manual compare shows comparison table", async ({ page }) => {
    await mockCompareApi(page);

    await page.goto("/compare");

    await page.getByLabel("Item IDs (comma separated)").fill("flight-1, flight-2");
    await page.getByRole("button", { name: "Compare" }).click();

    await expect(page.getByRole("table", { name: "Price comparison table" })).toBeVisible();
    await expect(page.getByText("TPE → NRT (CI100)")).toBeVisible();
    await expect(page.getByText("TPE → NRT (BR198)")).toBeVisible();
  });

  test("loading spinner during API call", async ({ page }) => {
    let resolveCompare!: () => void;
    const comparePromise = new Promise<void>((r) => { resolveCompare = r; });

    await page.route("**/api/compare", async (route) => {
      await comparePromise;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_COMPARE_RESULTS),
      });
    });

    await page.goto("/compare");

    await page.getByLabel("Item IDs (comma separated)").fill("flight-1, flight-2");
    await page.getByRole("button", { name: "Compare" }).click();

    await expect(page.getByLabel("Loading comparison...")).toBeVisible();

    resolveCompare();

    await expect(page.getByRole("table", { name: "Price comparison table" })).toBeVisible();
  });

  test("error alert on API failure", async ({ page }) => {
    await mockApiError(page, "**/api/compare", 500, "Comparison failed");

    await page.goto("/compare");

    await page.getByLabel("Item IDs (comma separated)").fill("flight-1, flight-2");
    await page.getByRole("button", { name: "Compare" }).click();

    await expect(page.getByText("Comparison failed")).toBeVisible();
  });

  test("Compare button does nothing with fewer than 2 IDs", async ({ page }) => {
    await mockCompareApi(page);

    await page.goto("/compare");

    await page.getByLabel("Item IDs (comma separated)").fill("flight-1");
    await page.getByRole("button", { name: "Compare" }).click();

    // No table, no error — nothing happens
    await expect(page.getByRole("table")).not.toBeVisible();
  });

  test("type selector switches flights and hotels", async ({ page }) => {
    await page.goto("/compare");

    const typeSelect = page.getByLabel("Type");

    await expect(typeSelect).toHaveValue("flight");

    await typeSelect.selectOption("hotel");
    await expect(typeSelect).toHaveValue("hotel");

    await typeSelect.selectOption("flight");
    await expect(typeSelect).toHaveValue("flight");
  });

  test("table highlights lowest price", async ({ page }) => {
    const results = [
      {
        item_id: "f-1",
        item_type: "flight",
        label: "Flight A",
        prices: [
          { provider: "amadeus", price: 15000, currency: "TWD", fetched_at: "2026-04-01T00:00:00Z" },
          { provider: "skyscanner", price: 13000, currency: "TWD", fetched_at: "2026-04-01T00:00:00Z" },
        ],
        lowest_price: 13000,
        highest_price: 15000,
        average_price: 14000,
      },
    ];

    await page.route("**/api/compare", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(results),
      })
    );

    await page.goto("/compare");

    await page.getByLabel("Item IDs (comma separated)").fill("f-1, f-2");
    await page.getByRole("button", { name: "Compare" }).click();

    await expect(page.getByRole("table")).toBeVisible();
    await expect(page.getByText("Flight A")).toBeVisible();
  });

  test("hotel compare with hotel type", async ({ page }) => {
    await page.route("**/api/compare", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_HOTEL_COMPARE_RESULTS),
      })
    );

    await page.goto("/compare");

    await page.getByLabel("Type").selectOption("hotel");
    await page.getByLabel("Item IDs (comma separated)").fill("hotel-1, hotel-2");
    await page.getByRole("button", { name: "Compare" }).click();

    await expect(page.getByRole("table")).toBeVisible();
    await expect(page.getByText("Grand Tokyo Hotel")).toBeVisible();
    await expect(page.getByText("Shinjuku Inn")).toBeVisible();
  });
});
