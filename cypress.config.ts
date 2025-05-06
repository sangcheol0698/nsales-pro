import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    specPattern: 'e2e/specs/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'e2e/support/e2e.ts',
    fixturesFolder: 'e2e/fixtures',
    screenshotsFolder: 'e2e/screenshots',
    videosFolder: 'e2e/videos',
    downloadsFolder: 'e2e/downloads',
  },
  component: {
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
    specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'e2e/support/component.ts',
  },
});