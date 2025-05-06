import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';
import { configDefaults, defineConfig as defineVitestConfig } from 'vitest/config';
import { fileURLToPath } from 'node:url';

// Vite configuration
const viteConfig = defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
});

// Vitest configuration
const vitestConfig = defineVitestConfig({
  test: {
    environment: 'jsdom',
    exclude: [...configDefaults.exclude, 'e2e/*'],
    root: '.',
    testTransformMode: {
      web: ['.[jt]sx'],
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/test/'],
    },
  },
});

// Merge configurations
export default {
  ...viteConfig,
  test: vitestConfig.test,
};
