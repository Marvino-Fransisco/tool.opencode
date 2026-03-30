---
name: fe-diagram-generation
description: Use this skill when the frontend agent needs to produce visual diagrams for a feature design. Triggers include: "draw the flow", "show the component tree", "diagram the state machine", "visualize the architecture", or whenever the design document needs a High Level Diagrams section. Always run after component-designer and state-designer, before markdown-formatter. Produces Mermaid diagrams (flowchart, sequence, stateDiagram, graph) that render in GitHub, Notion, and most markdown viewers.
---

This skill guides the agent to produce clear, accurate diagrams in Mermaid syntax that illustrate the feature's architecture, data flow, and state transitions.

## Goal

Produce diagrams that answer these questions visually:
1. **Component tree** — What renders what?
2. **Data flow** — Where does data come from and where does it go?
3. **User flow** — What are the steps from entry to goal?
4. **State machine** — What states does the feature move through?
5. **Sequence diagram** — How do the system components interact over time?

---

## Diagram Type Selection

| What to show | Diagram type | Mermaid keyword |
|---|---|---|
| Component parent-child relationships | Tree / Graph | `graph TD` |
| Data moving between layers | Flow / Graph | `graph LR` |
| User steps through a feature | Flowchart | `flowchart TD` |
| UI states and transitions | State machine | `stateDiagram-v2` |
| API request/response sequence | Sequence | `sequenceDiagram` |
| Page/screen navigation | Flowchart | `flowchart TD` |
| Decision logic | Flowchart | `flowchart TD` |

---

## Diagram 1 — Component Tree

Shows which components render which children.

```mermaid
graph TD
  A[ProductPage\nPage] --> B[ProductGrid\nFeature]
  A --> C[FilterPanel\nFeature]
  A --> D[Pagination\nUI]
  B --> E[ProductCard\nUI]
  B --> F[ProductCardSkeleton\nUI]
  C --> G[CategoryFilter\nUI]
  C --> H[PriceRangeFilter\nUI]

  style A fill:#1e3a5f,color:#7dd3fc
  style B fill:#1a3a2a,color:#6ee7b7
  style C fill:#1a3a2a,color:#6ee7b7
  style D fill:#2a1a3a,color:#c4b5fd
  style E fill:#2a1a3a,color:#c4b5fd
  style F fill:#2a1a3a,color:#c4b5fd
  style G fill:#2a1a3a,color:#c4b5fd
  style H fill:#2a1a3a,color:#c4b5fd
```

Rules:
- Pages at the top (blue)
- Feature/smart components in the middle (green)
- Pure UI components at the bottom (purple)
- Label each node with: `[ComponentName\nType]`

---

## Diagram 2 — Data Flow

Shows how data moves: API → hook → component → user action → mutation → API.

```mermaid
graph LR
  API[GET /api/products] -->|useProducts| Store[(React Query Cache)]
  Store -->|products[]| ProductGrid
  ProductGrid -->|product| ProductCard
  User([User]) -->|click Add to Cart| ProductCard
  ProductCard -->|onAddToCart| CartStore[(Zustand cartStore)]
  CartStore -->|POST /api/cart| CartAPI[POST /api/cart]
  CartAPI -->|invalidate cart| Store
```

Rules:
- APIs on the left
- Components in the middle
- User interactions and side effects on the right
- Label every arrow with what flows through it
- Use `[( )]` for data stores, `([ ])` for external actors (User, API)

---

## Diagram 3 — User Flow / Happy Path

Shows the steps a user takes from entry to goal completion.

```mermaid
flowchart TD
  Start([User lands on /products]) --> Load[Fetch products from API]
  Load --> Loading{Loading?}
  Loading -- Yes --> Skeleton[Show 12 product skeletons]
  Loading -- No --> HasData{Has products?}
  Skeleton --> HasData
  HasData -- No --> Empty[Show empty state\n+ Add Product CTA]
  HasData -- Yes --> Grid[Render ProductGrid]
  Grid --> Filter[User applies filters]
  Filter --> Refetch[Refetch with new params]
  Refetch --> Grid
  Grid --> Card[User clicks ProductCard]
  Card --> Cart[addToCart mutation fires]
  Cart --> Success[Toast: Added to cart!]
  Cart --> Error[Toast: Couldn't add — retry]
```

Rules:
- Start with `([...])` rounded stadium shape
- Decision points with `{...}` diamond shape
- Normal steps with `[...]` rectangle
- End states with `((...))` circle
- Label every branch clearly

---

## Diagram 4 — State Machine

Shows the states a component or feature moves through.

```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> Loading: User submits form
  Loading --> Success: API returns 200
  Loading --> Error: API returns 4xx/5xx
  Loading --> Timeout: No response after 10s
  Success --> Idle: User starts new action
  Error --> Idle: User dismisses error
  Error --> Loading: User clicks Retry
  Timeout --> Error: Show timeout message
```

Rules:
- Start with `[*]`
- Label every transition with the event that triggers it
- Include error and timeout states — not just happy path
- Keep states noun-like: `Idle`, `Loading`, `Success`, `Error`

---

## Diagram 5 — Sequence Diagram

Shows the order of interactions between the user, components, and APIs over time.

```mermaid
sequenceDiagram
  actor User
  participant Page as ProductPage
  participant Hook as useProducts
  participant Cache as React Query
  participant API as GET /api/products

  User->>Page: Navigates to /products
  Page->>Hook: mount → useProducts(filters)
  Hook->>Cache: Check cache for ['products', filters]
  alt Cache miss or stale
    Cache->>API: GET /api/products?...
    API-->>Cache: 200 { items: Product[] }
    Cache-->>Hook: fresh data
  else Cache hit
    Cache-->>Hook: cached data (instant)
  end
  Hook-->>Page: { data, isLoading, error }
  Page-->>User: Render ProductGrid or Skeleton
```

Rules:
- Actors on the left (`actor User`)
- Services/components as `participant`
- Use `-->>` for responses (dashed), `->>` for requests (solid)
- Use `alt/else/end` for conditional paths
- Keep to 5–8 participants maximum

---

## Mermaid Syntax Rules

```
DO:
- Use descriptive node labels
- Add \n for line breaks in node labels
- Keep diagrams focused (one concern per diagram)
- Test diagrams render correctly before including

DON'T:
- Use special characters in node IDs (stick to alphanumeric)
- Make one diagram show everything (split into multiple)
- Use >4 levels of nesting in graph diagrams
- Forget to close all subgraph blocks
```

---

## Output Format

For each diagram, output:

````
### [Diagram Name]

[One sentence describing what this diagram shows]

```mermaid
[diagram code]
```
````

Always produce at minimum:
1. **Component Tree** — for any feature with more than 2 components
2. **User Flow** — for any feature with user interaction steps
3. **State Machine** — for any feature with async operations (loading/error/success)

Optionally add:
4. **Data Flow** — when state management is complex
5. **Sequence Diagram** — when API interaction sequence matters

---

## Labeling Conventions

| Element | Convention |
|---|---|
| Page component | `[ComponentName\n(Page)]` |
| Feature/smart component | `[ComponentName\n(Feature)]` |
| UI/presentational component | `[ComponentName\n(UI)]` |
| API endpoint | `[METHOD /path]` |
| Data store | `[(StoreName)]` |
| User / external actor | `([User])` |
| Decision | `{Condition?}` |
| Terminal state | `((Done))` |