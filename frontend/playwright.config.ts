import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  reporter: 'list',
  timeout: 60000,
  expect: { timeout: 10000 },
  use: {
    baseURL: process.env.ASSETGEN_FRONTEND_URL || 'http://127.0.0.1:5173',
    headless: true,
    screenshot: 'only-on-failure',
    launchOptions: process.env.PLAYWRIGHT_CHANNEL
      ? { channel: process.env.PLAYWRIGHT_CHANNEL }
      : undefined,
  },
});
