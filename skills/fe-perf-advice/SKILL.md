---
name: fe-perf-advice
description: Use this skill when the frontend agent needs to identify and mitigate performance risks in a feature design. Triggers include: any feature with lists, data tables, infinite scroll, images, heavy computation, real-time updates, or complex forms. Also triggers for "optimize this", "it's slow", "too many re-renders", "bundle too large". Always run after component-designer and state-designer. Output fills the "Performance Considerations" section of the design document.
---

This skill guides the agent to identify performance risks early, during design, before they become production problems.

## Goal

Produce a **Performance Risk Register** with mitigations for:
1. Render performance (unnecessary re-renders, slow components)
2. Network performance (waterfalls, over-fetching, large payloads)
3. Bundle performance (large dependencies, unoptimized code splitting)

---

## Tier 1 — Render Performance

### Re-render Analysis

For every component in the tree, ask: "What causes this to re-render?"

A component re-renders when:
- Its own state changes
- Its parent re-renders (and passes new props)
- A context it consumes changes
- A store it subscribes to updates

**High-risk patterns**:

| Pattern | Problem | Fix |
|---|---|---|
| Object/array created inline as prop | New reference every render | `useMemo` or extract outside component |
| Callback created inline as prop | New reference every render | `useCallback` |
| Component subscribes to entire store | Rerenders on any store update | Use selectors (`useStore(s => s.specificField)`) |
| List renders 100+ items | DOM nodes are expensive | Virtualize with `@tanstack/react-virtual` |
| Expensive calculation in render | Blocks every paint | `useMemo` with correct deps |
| Context with many consumers | One update triggers all | Split contexts by update frequency |

**Memoization rules**:
- `React.memo`: wrap a component only if it receives stable props and re-renders expensively
- `useMemo`: only for computations that are measurably slow (>1ms) — don't premature-optimize
- `useCallback`: useful when a callback is a dependency of `useEffect` or passed to `React.memo` children
- **Don't memoize everything** — it has overhead and makes code harder to read

### Virtualization Threshold

| Item Count | Action |
|---|---|
| < 50 items | No virtualization needed |
| 50–200 items | Consider virtualization if items are complex |
| 200+ items | Always virtualize |
| Infinite scroll | Always virtualize |

---

## Tier 2 — Network Performance

### Identify Request Waterfalls

A waterfall occurs when requests are sequential but could be parallel.

Diagram every data dependency:
```
Page loads
  → fetch user (needed for next request)
    → fetch user's products (depends on userId)
      → fetch product details (depends on productId)
```

Fix: Parallel fetch where data isn't dependent. Prefetch on hover/navigation.

### Over-fetching

Check API responses — are components receiving more data than they display?

- **GraphQL**: Specify exact fields needed
- **REST**: Check if pagination is implemented (`?limit=20&page=1`)
- **Large payloads**: Add response compression (gzip/brotli — usually server config)
- **Images**: Always specify dimensions, use `loading="lazy"` for below-the-fold

### Caching Strategy

| Data Type | Cache Strategy |
|---|---|
| Static content (docs, config) | Long stale time (1 hour+) |
| User profile | Medium stale time (5 min), refetch on focus |
| Feed / list data | Short stale time (30–60s) or manual invalidation |
| Real-time data | No cache — use WebSocket or polling |
| Search results | Cache by query key, stale after 30s |

### Request Deduplication

If multiple components mount at the same time and all fetch the same data:
- React Query / SWR deduplicates by default — verify the cache key is identical across all callers
- If using manual fetch: wrap in a shared hook so the request is made once

### Debounce / Throttle

| Scenario | Strategy | Delay |
|---|---|---|
| Search input | Debounce | 300ms |
| Window resize handler | Throttle | 100ms |
| Scroll handler | Throttle | 16ms (1 frame) |
| Auto-save form | Debounce | 1000ms |
| Real-time validation | Debounce | 500ms |

---

## Tier 3 — Bundle Performance

### Code Splitting

For every new route or heavy component, ask: "Should this be lazy-loaded?"

```ts
// Lazy load routes
const ProductPage = lazy(() => import('./features/products/ProductPage'));

// Lazy load heavy components (charts, maps, rich text editors)
const ChartWidget = lazy(() => import('./components/ChartWidget'));
```

**When to lazy-load**:
- Every route (always)
- Components > 50KB that aren't in the initial viewport
- Third-party libraries only used in specific features (charts, maps, date pickers)
- Admin/settings pages rarely visited by most users

**When NOT to lazy-load**:
- Components in the critical rendering path
- Components visible immediately on page load
- Small components (not worth the overhead)

### Dependency Audit

For each new `import` added by this feature:

```bash
# Check bundle impact before adding
npx bundlephobia [package-name]
```

Watch for:
- Libraries that pull in large peer dependencies (moment.js → use date-fns)
- Libraries duplicating things React already provides
- Multiple similar libraries already in the project

### Image Optimization

| Scenario | Strategy |
|---|---|
| User avatars | Serve at display size, use WebP |
| Product images | Responsive `srcset`, lazy load below fold |
| Icons | SVG sprites or icon font, never PNG |
| Hero images | `loading="eager"`, highest priority, serve WebP with JPEG fallback |
| Generated/dynamic | Use CDN image transformation (Cloudinary, imgix) |

---

## Step-by-Step for Any Feature

1. List all components → flag any rendering 50+ items
2. Map all data requests → identify waterfalls and redundant fetches
3. List all new npm packages → check bundle size
4. Identify user interactions with rapid events (scroll, type, resize) → add debounce/throttle
5. Identify any new routes → add lazy loading
6. Check for inline object/array/function props → memoize where needed

## Output Format

```
## Performance Considerations

### Render Risks

| Component | Risk | Mitigation |
|-----------|------|------------|
| [Name] | [risk description] | [fix] |

### Network Risks

| Operation | Risk | Mitigation |
|-----------|------|------------|
| [fetch X] | [waterfall / over-fetch / etc] | [fix] |

### Bundle Risks

| Addition | Estimated Size | Action |
|----------|---------------|--------|
| [package] | [KB] | [lazy load / tree-shake / replace] |

### Optimization Checklist
- [ ] Virtualize [ComponentName] (renders [N] items)
- [ ] Debounce [handler] (300ms)
- [ ] Lazy load [Route/Component]
- [ ] Memoize [expensive computation] in [Component]
- [ ] Parallel fetch [requestA] and [requestB] — they don't depend on each other
- [ ] Add pagination to [endpoint] (currently returns all records)
```

## Anti-Patterns to Avoid

- **Premature optimization**: Don't add `useMemo` everywhere — measure first
- **Over-splitting**: Lazy loading tiny components adds more overhead than it saves
- **Ignoring network**: Most perf problems are network, not render
- **Unthrottled event handlers**: Scroll and resize handlers fire 60x/second
- **Not paginating**: Never fetch unlimited records from an API