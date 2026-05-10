const { test, expect } = require("@playwright/test");

const credentials = {
  username: "qa.admin",
  password: "pass12345",
};

async function login(page) {
  await page.goto("/login/");
  await page.fill('input[name="username"]', credentials.username);
  await page.fill('input[name="password"]', credentials.password);
  await page.click('.app-form button[type="submit"], .app-form input[type="submit"]');
  await expect(page.locator(".app-rail")).toBeVisible();
}

async function expectNoDocumentOverflow(page) {
  const overflow = await page.evaluate(() => {
    return document.documentElement.scrollWidth > document.documentElement.clientWidth;
  });
  expect(overflow).toBeFalsy();
}

async function expectNoRailOverflow(page) {
  const overflow = await page.evaluate(() => {
    const rail = document.querySelector(".app-rail");
    return rail ? rail.scrollWidth > rail.clientWidth : false;
  });
  expect(overflow).toBeFalsy();
}

test("public home renders without document overflow", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("body")).toBeVisible();
  await expectNoDocumentOverflow(page);
});

test("login page renders usable form", async ({ page }) => {
  await page.goto("/login/");
  await expect(page.locator('input[name="username"]')).toBeVisible();
  await expect(page.locator('input[name="password"]')).toBeVisible();
  await expectNoDocumentOverflow(page);
});

test("authenticated dashboard sidebar filters without rail overflow", async ({ page }) => {
  await login(page);

  const filter = page.locator("#navSearchInput");
  await expect(filter).toBeVisible();
  await filter.fill("enrollments");
  await expect(page.locator(".nav-shell")).toBeVisible();
  await expectNoRailOverflow(page);
});

test("detail page tabs switch content", async ({ page }) => {
  await login(page);
  await page.goto("/factions/qa-eagle-patrol");

  const tabs = page.locator('[data-bs-toggle="tab"]');
  await expect(tabs.first()).toBeVisible();

  const count = await tabs.count();
  expect(count).toBeGreaterThan(1);

  await tabs.nth(1).click();
  await expect(tabs.nth(1)).toHaveClass(/active/);
  await expect(page.locator(".tab-pane.active")).toBeVisible();
});

test("manual report table filtering works", async ({ page }) => {
  await login(page);
  await page.goto("/reports/builtin/faction-enrollments/?unscoped=1");

  await expect(page.getByRole("heading", { name: "Faction Enrollments", level: 2 })).toBeVisible();
  await expect(page.locator(".table-shell table")).toBeVisible();

  const filter = page.locator("#reportResultFilter");
  await expect(filter).toBeVisible();
  await filter.fill("qa eagle");
  await expect(page.locator("[data-table-count]")).toContainText(/rows|row/);

  await filter.fill("no-such-row-value");
  await expect(page.locator("[data-filter-empty]")).toBeVisible();
});

test("theme toggle remains navigable", async ({ page }) => {
  await login(page);
  await page.goto("/dashboard/");

  const toggle = page.locator(".theme-toggle-form button");
  await expect(toggle).toBeVisible();
  await toggle.click();
  await expect(page.locator("body.app-shell")).toBeVisible();
});

test("mobile sidebar opens and stays within viewport", async ({ page, isMobile }) => {
  test.skip(!isMobile, "mobile-only sidebar coverage");
  await login(page);

  const toggle = page.locator("#mobileRailToggle");
  await expect(toggle).toBeVisible();
  await toggle.click();
  await expect(page.locator(".app-rail")).toBeVisible();
  await expectNoRailOverflow(page);
});
