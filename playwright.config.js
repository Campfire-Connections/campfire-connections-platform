const { defineConfig, devices } = require("@playwright/test");

const host = "127.0.0.1";
const port = process.env.PLAYWRIGHT_PORT || "8000";
const baseURL = `http://${host}:${port}`;
const python = process.env.PYTHON || ".venv/bin/python";

module.exports = defineConfig({
  testDir: "./tests/browser",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  webServer: {
    command: `${python} manage.py migrate --noinput && ${python} scripts/seed-browser-qa.py && ${python} manage.py runserver ${host}:${port} --noreload`,
    url: baseURL,
    reuseExistingServer: false,
    timeout: 120000,
  },
  use: {
    baseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
});
