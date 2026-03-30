---
name: fe-project-read
description: Use this skill when the frontend agent needs to understand a project's file structure before designing a feature. Triggers include: any new design task, "read the project", "understand the codebase", "scan the tree", or whenever the agent is starting fresh on an unfamiliar repo. Reads the file tree, identifies code-logic-relevant paths, and ignores noise (node_modules, dist, build, .git, assets, public). Do NOT use for reading file contents — this skill maps structure only.
---

This skill guides the agent to efficiently map a project's file tree, extracting only the structure that matters for frontend design decisions.

## Goal

Produce a clean, annotated project tree that answers:
- Where is the source code?
- How are features/pages organized?
- What routing pattern is used?
- Where do components, hooks, stores, and utils live?

## Step 1 — Initial Scan

Run a tree command, excluding noise directories:

```bash
find . -type f \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -not -path "*/coverage/*" \
  -not -path "*/.next/*" \
  -not -path "*/out/*" \
  -not -path "*/public/static/*" \
  | sort | head -120
```

Or if `tree` is available:

```bash
tree -I "node_modules|dist|build|.git|coverage|.next|out" -L 4 --dirsfirst
```

## Step 2 — Identify Key Directories

After the scan, categorize what you find. Look for these canonical patterns:

| Directory Pattern | Meaning |
|---|---|
| `src/pages/` or `app/` | Routing root (Next.js / Remix / Vite) |
| `src/components/` | Shared/global components |
| `src/features/` or `src/modules/` | Feature-sliced architecture |
| `src/hooks/` | Custom React hooks |
| `src/store/` or `src/stores/` | State management |
| `src/lib/` or `src/utils/` | Utilities and helpers |
| `src/api/` or `src/services/` | API layer |
| `src/types/` | TypeScript types |
| `src/styles/` or `src/theme/` | Design tokens / global styles |

## Step 3 — Surface the Right Files

After mapping directories, identify the **5–10 most relevant files** for the current design task:

- The entry point (`main.tsx`, `App.tsx`, `_app.tsx`)
- The router config (if any)
- An existing feature file that is similar to what needs to be built
- The global state store (if it exists)
- The API client setup

Do NOT read all files. Only read the ones that answer "what patterns exist that the new feature must follow?"

## Step 4 — Output a Structured Summary

Produce output in this format:

```
## Project Tree Summary

Root: [detected root path]
Framework: [React / Next.js / Vue / etc — inferred]
Language: [TypeScript / JavaScript]

### Source Structure
src/
  pages/          → Route-based page components
  components/     → Shared UI components
  features/       → Feature modules (auth, dashboard, …)
  hooks/          → Custom hooks
  store/          → Zustand / Redux store
  api/            → API client and service functions
  types/          → Shared TypeScript interfaces

### Entry Points
- [file path] → [what it does]

### Most Relevant Existing Feature
- [feature path] → [why it's relevant to current task]

### Notes
- [anything unusual or worth flagging]
```

## What to Ignore

Never waste tokens describing:
- `node_modules` contents
- `dist` / `build` outputs
- Test fixture files unless the task involves testing
- `public/` static asset folders
- Lock files (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`)
- `.env` files

## Edge Cases

- **Monorepo**: If you detect `packages/` or `apps/` at root, identify which workspace is relevant to the task before scanning deeper.
- **No `src/`**: Some projects put code at root. Look for `pages/`, `components/`, or `app/` at the top level.
- **Flat structure**: If everything is at one level with no subdirectories, note this — it's important pattern information.
- **Unknown framework**: Check `package.json` `dependencies` to infer the stack before guessing.