import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';
import { configDefaults, defineConfig as defineVitestConfig } from 'vitest/config';
import { fileURLToPath } from 'node:url';
import babel from 'vite-plugin-babel';

// Vite configuration
const viteConfig = defineConfig({
  plugins: [
    vue(), 
    tailwindcss(),
    babel({
      include: ['src/**/*.ts'],
      exclude: ['node_modules/**']
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  define: {
    __METADATA__: true,
  },
  esbuild: {
    target: 'es2022',
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
