import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: 'e2e-playwright/specs',
  timeout: 30000,
  expect: { timeout: 5000 },
  fullyParallel: true,
  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'VITE_E2E_BYPASS_AUTH=true vite',
    url: process.env.PW_BASE_URL || 'http://localhost:5173',
    reuseExistingServer: false,
    timeout: 120000,
  },
  use: {
    baseURL: process.env.PW_BASE_URL || 'http://localhost:5173',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
    viewport: { width: 1440, height: 900 },
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
