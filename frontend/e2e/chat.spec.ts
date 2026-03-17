import { test, expect } from "@playwright/test";
import { setupAuthenticated } from "./helpers";

test.describe("Chat page", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticated(page);
  });

  test("shows coming soon message", async ({ page }) => {
    await page.goto("/chat");

    await expect(page.getByText("AI Chat — Coming Soon")).toBeVisible();
    await expect(
      page.getByText("Chat feature is temporarily unavailable")
    ).toBeVisible();
  });

  test("has link back to home", async ({ page }) => {
    await page.goto("/chat");

    const backLink = page.getByRole("link", { name: "Back to Home" });
    await expect(backLink).toBeVisible();
    await backLink.click();
    await expect(page).toHaveURL("/");
  });
});
