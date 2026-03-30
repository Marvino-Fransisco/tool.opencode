---
name: fe-component-design
description: Use this skill when the frontend agent needs to design the component structure for a feature. Triggers include: designing any UI, "what components do I need", "break this into components", any task requiring a component tree, responsibility mapping, or props interface design. Always run after request-analyser. Output fills the "UI / Component Structure" section of the design document. Follow the pattern-detector output — never invent new patterns unless asked.
---

This skill guides the agent to design a clear, reusable, well-scoped component tree before any code is written.

## Goal

Produce:
1. A **component tree** showing parent-child relationships
2. **Responsibility mapping** — what each component owns
3. **Props interfaces** — what data flows in and out
4. **Reusability assessment** — what's new vs what already exists

## Step 1 — Identify the Top-Level Container

Start with the page/route that hosts the feature. Ask:

- Is this a new route, a modal, a drawer, or a section within an existing page?
- What layout wraps it? (authenticated layout, full-width, sidebar layout)
- What data does the top-level container need to fetch?

The top-level component is always a **container** (data-aware). Everything below it should trend toward being **presentational** (data-unaware).

## Step 2 — Split by Responsibility

Apply the **Single Responsibility Principle** to each piece of UI:

For each visual block, ask: "Does this have one clear job?"

Common splits:
| Pattern | When to split |
|---|---|
| List vs List Item | List manages data; item manages display |
| Form vs Field | Form manages submission; field manages a single input |
| Page vs Section | Page manages layout; section manages a concern |
| Feature vs UI | Feature component has logic; UI component is pure |
| Container vs Skeleton | Container has real data; skeleton is the loading state |

## Step 3 — Classify Each Component

Label every component with one of these types:

- **Page** — Route-level component, fetches data, owns layout
- **Feature** — Smart component, contains business logic, connected to store/query
- **UI** — Dumb/presentational, receives all data via props, no side effects
- **Layout** — Structural wrapper (grid, split pane, sidebar)
- **Skeleton** — Loading placeholder, mirrors the shape of its real counterpart
- **Form** — Manages form state and submission logic
- **Modal/Drawer** — Overlay component with its own lifecycle

## Step 4 — Define Props Interfaces

For each component, define the TypeScript interface.

Rules:
- Props should be as narrow as possible (don't pass the whole entity if you only need `id` and `name`)
- Callbacks should be typed: `onSubmit: (data: FormData) => void`
- Optional props get `?` — document when/why they're optional
- Don't pass `setState` functions as props — pass callback handlers instead

Example format:
```ts
interface ProductCardProps {
  id: string;
  name: string;
  price: number;
  imageUrl?: string;           // optional: falls back to placeholder
  onAddToCart: (id: string) => void;
  isLoading?: boolean;         // shows skeleton when true
}
```

## Step 5 — Check for Reusability

Before declaring a new component, check:

1. Does this component exist in the design system / component library already?
2. Does a similar component exist elsewhere in the codebase? (check `src/components/`)
3. Should this new component be added to the shared components folder?

Classify each component as:
- **Reuse existing**: [name and location of existing component]
- **Extend existing**: [name] + [what prop/variant to add]
- **New shared**: goes into `src/components/` — usable by other features
- **New local**: specific to this feature, lives in `src/features/featureName/`

## Step 6 — Map Data Flow

For each component, identify what data it needs and where it comes from:

```
FeaturePage (fetches: useProductList)
  └── ProductGrid (props: products[], isLoading)
       └── ProductCard (props: product, onAddToCart)
  └── CartSummary (reads: cartStore)
       └── CartItem (props: item, onRemove)
  └── CheckoutButton (reads: cartStore.total, calls: cartStore.checkout)
```

Arrows of data flow:
- **Down**: parent passes props to children
- **Up**: children call callback handlers from parent
- **Store**: component reads from / writes to global store directly
- **Query**: component owns a `useQuery` / `useSWR` call

## Output Format

```
## Component Structure

### Component Tree
[FeaturePage] (Page)
  ├── [ComponentA] (Feature) — owns: [concern]
  │     ├── [ComponentB] (UI) — displays: [data]
  │     └── [ComponentC] (UI) — displays: [data]
  ├── [ComponentD] (Form) — manages: [form concern]
  └── [ComponentE] (Skeleton) — shown when: [loading condition]

### Component Responsibilities

| Component | Type | Responsibility | Data Source |
|-----------|------|---------------|-------------|
| [Name] | Page | [what it does] | [API / store / props] |
| [Name] | Feature | [what it does] | [API / store / props] |
| [Name] | UI | [what it does] | props only |

### Props Interfaces

\`\`\`ts
// [ComponentName]
interface [ComponentName]Props {
  [prop]: [type]; // [why]
}
\`\`\`

### Reusability Map

| Component | Status | Notes |
|-----------|--------|-------|
| [Name] | Reuse existing | [location] |
| [Name] | New shared | [why it belongs in shared] |
| [Name] | New local | [why it's feature-specific] |

### Data Flow Diagram
[ASCII or described tree showing data movement]
```

## Anti-Patterns to Avoid

- **Prop drilling beyond 2 levels**: If data passes through 3+ components untouched, use a store or context
- **God component**: If a component does more than 3 things, split it
- **Premature abstraction**: Don't create a shared component for something used once
- **Naming ambiguity**: `UserCard` and `UserProfile` in the same codebase will cause confusion — be specific
- **Logic in UI components**: UI components should have zero `useEffect`, `useState` for business logic, or API calls