# Frontend Review (May 2, 2026)

## What I checked

- Project structure and stack sanity (`frontend/package.json`).
- API/auth integration (`frontend/src/services/api.ts`, `frontend/src/context/AuthContext.tsx`).
- Main mission workflow surface (`frontend/src/pages/CommandDeck.tsx`).
- Lint readiness (`npm run lint`).

## Findings

### 1) Fixed: AuthContext imported `api` incorrectly

`AuthContext.tsx` used a named import (`{ api }`) even though `api.ts` only exports Axios as the default export.

- Impact: runtime/build error depending on bundler/TS checks; auth header injection would fail.
- Fix: switched to default import.

### 2) Tooling gap: lint config depends on a missing package

`eslint.config.js` imports `typescript-eslint`, but this package is not currently installable in the environment (registry returned 403 during install attempt).

- Impact: `npm run lint` fails before source linting starts.
- Recommendation: ensure `typescript-eslint` is added to `devDependencies` and available in your package registry policy, or adapt config to installed `@typescript-eslint/*` packages.

### 3) Architectural observations

- `api.ts` and `AuthContext.tsx` currently mix two token strategies (localStorage interceptor + in-memory context token). Consider converging on a single source-of-truth to avoid stale/competing auth headers.
- `CommandDeck.tsx` uses `any[]` for `recentMissions` and has inline style-heavy JSX; extracting typed view models + style modules would improve maintainability as the page evolves.

## Overall assessment

- The frontend direction is solid and feature-rich, but should prioritize **tooling reliability** (lint/type gates) and **auth consistency** before scaling more UI complexity.
