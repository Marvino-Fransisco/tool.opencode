---
name: fe-pattern-detection
description: Use this skill when the frontend agent needs to understand HOW a project is written before designing a new feature. Triggers include: "understand the pattern", "follow existing conventions", any design task where the agent must stay consistent with existing code. Detects stack, naming conventions, state management approach, component patterns, styling system, and data-fetching patterns. Always run AFTER project-reader. Output feeds into every design decision.
---

This skill teaches the agent to read existing code and extract the conventions that all new features must follow.

## Goal

Produce a **Pattern Profile** — a concise reference that answers:
- What does a typical component look like?
- How is state managed?
- How are API calls made?
- What naming and file conventions are used?
- What styling system is in use?

## Step 1 — Detect the Stack

Check `package.json` dependencies:

```bash
cat package.json | grep -E '"(react|vue|svelte|next|nuxt|remix|vite|typescript|tailwind|styled-components|emotion|zustand|redux|jotai|recoil|react-query|swr|axios|zod|yup)"'
```

Map findings to stack profile:

| Package | Implication |
|---|---|
| `next` | Next.js — check for App Router (`app/`) vs Pages Router (`pages/`) |
| `react-router-dom` | SPA with client-side routing |
| `tailwindcss` | Utility-first CSS — look for `cn()` or `clsx` usage |
| `styled-components` / `@emotion/styled` | CSS-in-JS |
| `zustand` | Lightweight atom stores |
| `@reduxjs/toolkit` | Redux with slices |
| `@tanstack/react-query` | Server state, async caching |
| `swr` | Data fetching with revalidation |
| `zod` | Schema validation — check where schemas live |
| `axios` | HTTP client — look for interceptor setup |

## Step 2 — Read One Representative Component

Pick an existing feature component (not a trivial UI primitive). Read it fully:

```bash
cat src/features/[some-feature]/[SomeComponent].tsx
```

Extract:
- **Props pattern**: Are props typed inline, or with a separate `interface Props`?
- **Default exports vs named exports**: Which is used?
- **Hook usage**: Are hooks inline in the component or extracted to `use*.ts` files?
- **Error handling**: try/catch? Error boundaries? Toast notifications?
- **Conditional rendering**: Ternary? Early returns? Switch?
- **Event handlers**: Inline arrows? Named functions? Callbacks passed down?

## Step 3 — Read the State Store (if any)

```bash
cat src/store/*.ts   # Zustand
cat src/store/*Slice.ts  # Redux
cat src/context/*.tsx    # Context API
```

Extract:
- How are stores structured? One big store or many small ones?
- Are selectors used? Memoized?
- How are async actions handled? (thunk, middleware, mutation)

## Step 4 — Read an API Call

```bash
cat src/api/*.ts
cat src/services/*.ts
cat src/lib/api*.ts
```

Extract:
- Is there a base client (axios instance / fetch wrapper)?
- Are API functions standalone or part of React Query hooks?
- Where does error handling live — in the API layer or the component?
- Is there a response type wrapper (e.g., `ApiResponse<T>`)?

## Step 5 — Detect Naming Conventions

Scan file names for patterns:

```bash
find src -type f -name "*.tsx" | head -30
find src -type f -name "*.ts" | head -20
```

Look for:
- **Component files**: `PascalCase.tsx` or `kebab-case.tsx`?
- **Hook files**: `useSomething.ts` or `use-something.ts`?
- **Test files**: `.test.tsx`, `.spec.tsx`, or `__tests__/` folder?
- **Index files**: Does each folder have an `index.ts` barrel export?
- **Co-location**: Are styles/tests next to components or in separate folders?

## Step 6 — Output the Pattern Profile

```
## Pattern Profile

### Stack
- Framework: [Next.js 14 App Router / CRA / Vite + React / etc]
- Language: [TypeScript strict / TypeScript loose / JavaScript]
- Styling: [Tailwind + clsx / CSS Modules / styled-components / etc]
- State (client): [Zustand / Redux Toolkit / Context / useState only]
- State (server): [React Query / SWR / manual fetch / etc]
- Validation: [Zod / Yup / none]
- HTTP: [Axios with base client / native fetch / etc]

### Component Pattern
- Export style: [default export / named export]
- Props typing: [inline interface / external Props type / etc]
- Hooks: [inline in component / extracted to use*.ts]
- Error handling: [try/catch in component / error boundary / toast util]
- Example skeleton:

\`\`\`tsx
// [paste a minimal representative component skeleton]
\`\`\`

### State Pattern
- Store structure: [one file per domain / single store / etc]
- Async: [how async is handled]
- Example slice/store:

\`\`\`ts
// [paste a minimal representative store skeleton]
\`\`\`

### API Pattern
- Base client: [yes/no + location]
- Function style: [standalone async fn / React Query hook / etc]
- Error type: [ApiError type / plain Error / etc]
- Example:

\`\`\`ts
// [paste a minimal representative API call skeleton]
\`\`\`

### Naming Conventions
- Components: [PascalCase.tsx]
- Hooks: [useSomething.ts]
- Stores: [somethingStore.ts]
- API: [something.api.ts]
- Tests: [Something.test.tsx]
- Barrel exports: [yes / no]

### Folder Convention
- New feature goes in: [src/features/featureName/]
- Expected files: [Component.tsx, useComponent.ts, component.api.ts, types.ts]

### Flags / Anomalies
- [Anything inconsistent or worth noting]
```

## Critical Rule

**Never invent patterns.** If the codebase uses `useState` + prop drilling, the new feature should too — unless the user explicitly asks to improve. Document what exists, not what you'd prefer.