# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).

## Code Formatting

This project uses [Prettier](https://prettier.io/) for code formatting. Prettier is an opinionated code formatter that ensures consistent code style across the project.

### Prettier Configuration

The Prettier configuration is defined in `.prettierrc.json` with the following settings:
- Semi-colons at the end of statements
- Tab width of 2 spaces
- Print width of 100 characters
- Single quotes for strings
- ES5 trailing commas
- Bracket spacing
- No indentation for Vue script and style tags (to prevent extra line breaks)
- LF line endings

### ESLint Integration

Prettier is integrated with ESLint to ensure that code formatting issues are reported as ESLint errors. This integration is configured in `.eslintrc.js`.

### Available Scripts

The following npm scripts are available for formatting:

```bash
# Format all files in the src directory
npm run format

# Check if all files are formatted correctly
npm run format:check

# Format a specific file (example: main.ts)
npm run format:main
```
