# ui -- pathfinders-fyp

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin).

## Customize configuration

See [Vite Configuration Reference](https://vitejs.dev/config/).

## Project Setup

```sh
# npm
npm install
# pnpm
pnpm install
# yarn
yarn install
```

### Compile and Hot-Reload for Development

```sh
# npm
npm run dev
# pnpm
pnpm dev
# yarn
yarn dev
```

### Compile and Minify for Production

```sh
# npm
npm run build
# pnpm
pnpm build
# yarn
yarn build
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
# npm
npm run test:unit
# pnpm
pnpm test:unit
# yarn
yarn test:unit
```

### Run End-to-End Tests with [Playwright](https://playwright.dev)

```sh
# Install browsers for the first run
npx playwright install

# When testing on CI, must build the project first
npm run build
# Runs the end-to-end tests
npm run test:e2e
# Runs the tests only on Chromium
npm run test:e2e --project=chromium
# Runs the tests of a specific file
npm run test:e2e tests/example.spec.ts
# Runs the tests in debug mode
npm run test:e2e --debug
```

### Lint with [ESLint](https://eslint.org/)

```sh
# npm
npm run lint
# pnpm
pnpm lint
# yarn
yarn lint
```
