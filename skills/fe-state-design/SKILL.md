---
name: fe-state-design
description: Use this skill when the frontend agent needs to design the data and state layer for a feature. Triggers include: "where should state live", "how do I manage data", "design the store", "API integration", any feature involving fetched data, form state, shared state, or caching. Always run after request-analyser and alongside component-designer. Output fills the "Data & State" section of the design document. Follow the pattern-detector output strictly.
---

This skill guides the agent to make deliberate, consistent decisions about where state lives and how data flows through a feature.

## Goal

Produce:
1. A **state inventory** — every piece of state the feature needs
2. A **location decision** for each — where it lives and why
3. A **data flow map** — how state moves between layers
4. A **cache / freshness strategy** for server state

## The State Decision Framework

There are 4 types of state. Identify which type each piece of data is, then place it in the right location.

### Type 1 — UI State
Temporary, local, doesn't need to survive navigation.

Examples: `isOpen`, `activeTab`, `inputValue` (before submission), `isExpanded`

**Location**: `useState` inside the component that owns it.

Rule: If only one component needs it, it lives in that component. Period.

---

### Type 2 — Shared UI State
UI state needed by multiple components that aren't in a direct parent-child relationship.

Examples: sidebar collapsed state, active theme, modal open/close triggered from multiple places

**Location**:
- If 2–3 components: lift to nearest common ancestor
- If app-wide: lightweight global store (Zustand atom / Context)

---

### Type 3 — Server State (Async / Remote Data)
Data that lives on the server and is fetched asynchronously.

Examples: user profile, product list, order history, search results

**Location**: React Query / SWR / RTK Query (never `useState` + `useEffect` for this)

Key decisions:
- **Cache key**: What uniquely identifies this query? (`['products', filters]`)
- **Stale time**: How long before data is considered stale? (0s for real-time, 5min for mostly-static)
- **Refetch triggers**: On window focus? On interval? On user action only?
- **Optimistic updates**: Should the UI update before the server confirms?
- **Pagination**: Cursor-based or offset-based? Infinite scroll or paginated?

---

### Type 4 — Persisted / Global App State
State that must survive navigation, persist across sessions, or be shared across many features.

Examples: auth session, shopping cart, user preferences, notification count

**Location**: Global store (Zustand / Redux Toolkit) + localStorage/sessionStorage for persistence.

---

## Step 1 — Inventory All State

List every piece of data the feature needs. For each item:

```
| State | Type | Example Value | Owner |
|-------|------|--------------|-------|
| isModalOpen | UI State | false | ModalTrigger component |
| products | Server State | Product[] | useProducts hook |
| selectedFilters | Shared UI | { category: 'shoes' } | FiltersStore |
| cartItems | Global App | CartItem[] | cartStore |
```

## Step 2 — Make Location Decisions

For each piece of state, justify the location:

```
## State: selectedFilters
- Type: Shared UI State
- Lives in: Zustand filterStore (or URL search params)
- Why: Multiple components (FilterPanel, ProductGrid, ResultCount) read it
- Why not URL params: [reason if you chose store over URL]
- Why not Context: [pattern-detector showed Zustand is already used]
```

**Special consideration — URL as state**:
For anything a user might want to share, bookmark, or navigate back to:
- Search queries → URL param (`?q=shoes`)
- Filters → URL params (`?category=shoes&size=42`)
- Selected tab → URL hash or param
- Page number → URL param (`?page=2`)

## Step 3 — Design Server State Hooks

For each async data need, define the query hook:

```ts
// useProducts.ts
export function useProducts(filters: ProductFilters) {
  return useQuery({
    queryKey: ['products', filters],       // cache key includes filters
    queryFn: () => fetchProducts(filters),
    staleTime: 5 * 60 * 1000,             // 5 minutes
    select: (data) => data.items,          // transform here, not in component
    placeholderData: keepPreviousData,     // smooth pagination
  });
}
```

For mutations:

```ts
// useCreateProduct.ts
export function useCreateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] }); // refresh list
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });
}
```

## Step 4 — Design the Store (if needed)

If the feature requires shared or global state, define the store shape:

```ts
// Following pattern-detector output for Zustand:
interface FeatureStore {
  // State
  selectedId: string | null;
  
  // Derived (computed from state — don't store derived values)
  // selectedItem is derived: items.find(i => i.id === selectedId)
  
  // Actions
  setSelectedId: (id: string | null) => void;
  reset: () => void;
}
```

Rules:
- Never store derived values — compute them (with `useMemo` if expensive)
- Actions should be verbs: `setX`, `clearX`, `toggleX`, `submitX`
- One store per domain, not one giant global store
- Keep stores serializable (no functions, no DOM refs in state)

## Step 5 — Map State Updates

For every user action, trace the full state update path:

```
User clicks "Add to Cart"
  → onAddToCart(productId) called on ProductCard
  → cartStore.addItem(productId) called
  → cartStore state updates (optimistically)
  → useAddToCart mutation fires → POST /api/cart
  → On success: nothing (store already updated)
  → On error: cartStore.removeItem(productId) + toast.error()
```

## Output Format

```
## Data & State Design

### State Inventory

| State | Type | Location | Why |
|-------|------|---------|-----|
| [name] | [type] | [location] | [reason] |

### Server State Hooks

\`\`\`ts
// [hookName].ts
[hook definition]
\`\`\`

### Store Design (if needed)

\`\`\`ts
// [storeName].ts
[store interface + implementation skeleton]
\`\`\`

### State Update Flows

[User Action] → [Handler] → [State change] → [Side effects]

### Cache Strategy
- Stale time: [value + reason]
- Refetch triggers: [list]
- Optimistic updates: [yes/no + which mutations]
- Pagination: [strategy if needed]

### URL State
- [param name]: [what it stores, why in URL]
```

## Anti-Patterns to Avoid

- **`useEffect` for data fetching**: Use React Query / SWR instead
- **Storing derived state**: Never `setFullName(first + ' ' + last)` — compute it
- **Over-globalizing**: `isButtonHovered` should never be in a global store
- **Prop drilling through 3+ levels**: That's a sign state belongs higher or in a store
- **Mixing server and client state**: Keep server cache (React Query) separate from UI state (useState/Zustand)
- **Missing error state**: Every async operation needs an error state — never assume success