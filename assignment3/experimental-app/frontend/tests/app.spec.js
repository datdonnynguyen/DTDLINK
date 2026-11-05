import { test, expect } from "@playwright/test";

const input = (page) =>
  page.getByRole("textbox", { name: "Website URL", exact: true });
async function goTo(page, name) {
  const menu = page.getByRole("button", {
    name: "Open navigation",
    exact: true,
  });
  if (await menu.isVisible()) await menu.click();
  await page.getByRole("link", { name, exact: true }).click();
}

test("real prediction, input validation and anonymous session chart", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Analyse link", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("Enter a URL");
  await input(page).fill("https://paypal.com@account-check.example/login");
  await input(page).press("Enter");
  await expect(
    page.getByRole("heading", { name: "Potentially dangerous", exact: true }),
  ).toBeVisible();
  await expect(page.locator(".url-text a")).toHaveCount(0);
  await page
    .getByRole("combobox", { name: "Show signals", exact: true })
    .selectOption("high");
  await page
    .getByRole("button", { name: "Hidden destination", exact: true })
    .click();
  await expect(page.locator(".chart-detail").first()).toContainText(
    "Text before @ is not the real destination host.",
  );
  await goTo(page, "Session insights");
  await page.getByRole("button", { name: "Check #1", exact: true }).click();
  await expect(page.locator(".chart-detail").first()).toContainText("Check #1");
  await page
    .getByRole("combobox", { name: "Filter checks", exact: true })
    .selectOption("0");
  await expect(
    page.getByText("No checks match this filter.", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Clear session", exact: true })
    .click();
  await expect(
    page.getByText("Your first check starts the story.", { exact: true }),
  ).toBeVisible();
});

test("backend outage is shown as a useful error", async ({ page }) => {
  await page.route("**/predict", (route) => route.abort());
  await page.goto("/");
  await input(page).fill("https://example.com/");
  await input(page).press("Enter");
  await expect(page.getByRole("alert")).toContainText(
    "Cannot reach the analysis service",
  );
});

test("loading is visible and duplicate submissions are disabled", async ({
  page,
}) => {
  let release;
  const gate = new Promise((resolve) => {
    release = resolve;
  });
  await page.route("**/predict", async (route) => {
    await gate;
    await route.continue();
  });
  await page.goto("/");
  await input(page).fill("https://example.com/");
  await input(page).press("Enter");
  await expect(
    page.getByRole("button", { name: "Analysing…", exact: true }),
  ).toBeDisabled();
  await expect(
    page.getByText("Reading the signs in your link…", { exact: true }),
  ).toBeVisible();
  release();
  await expect(
    page.getByRole("heading", { name: "Potentially dangerous", exact: true }),
  ).toBeVisible();
});

test("unexpected render failure reaches the error boundary", async ({
  page,
}) => {
  await page.route("**/predict", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "{}" }),
  );
  await page.goto("/");
  await input(page).fill("https://example.com/");
  await input(page).press("Enter");
  await expect(
    page.getByRole("heading", {
      name: "Something unexpected happened.",
      exact: true,
    }),
  ).toBeVisible();
});

test("404 and phone layout remain usable", async ({ page }) => {
  await page.goto("/unknown-page");
  await expect(
    page.getByRole("heading", { name: "This page isn’t here.", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Back to Check URL", exact: true })
    .click();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});
