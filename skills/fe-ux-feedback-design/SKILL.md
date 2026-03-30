---
name: fe-ux-feedback-design
description: Use this skill when the frontend agent needs to design loading, error, success, and empty states for a feature. Triggers include: any async operation, form submission, data fetching, "what happens while loading", "how do I show errors", "empty state design", or any time the UI needs to communicate system status to the user. Always run after state-designer. Output fills the "UX / Feedback" section of the design document.
---

This skill guides the agent to design every non-happy-path state a user might encounter, ensuring the UI is never silent, confusing, or broken-looking.

## Core Principle

**The UI must always communicate what is happening.** A blank screen, an unresponsive button, or a silent failure are never acceptable. Every async operation has 4 states: loading, success, error, empty.

## The 4 Feedback States

### 1. Loading State

**Purpose**: Tell the user something is happening and progress isn't lost.

Decision tree:
```
Is this the initial page/component load?
  → Use skeleton (mirrors real content shape)

Is this a background refresh (data already showing)?
  → Use subtle loading indicator (spinner in corner, progress bar)

Is this a button action (user just clicked)?
  → Disable the button + show spinner inside it

Is this a full-page transition?
  → Use route-level loading (progress bar at top, e.g. NProgress)
```

**Skeleton rules**:
- Skeleton must match the shape and dimensions of real content
- Animate with a shimmer/pulse effect
- Show the same number of skeleton items as the expected result (or a sensible default like 3–5)
- Never use a plain spinner for content that has a known shape

**Button loading rules**:
- Disable immediately on click (prevent double-submission)
- Replace label with spinner + "Loading…" or keep label + add spinner
- Restore to original state on success or failure
- Set a timeout (e.g. 30s) — if no response, show error + re-enable

---

### 2. Success State

**Purpose**: Confirm the action completed. Don't overdo it.

Decision tree:
```
Was this a form submission?
  → Toast notification (3–5 seconds) + optionally redirect

Was this a destructive action (delete)?
  → Toast with undo option (5–7 seconds)

Was this a background sync?
  → Subtle indicator only (no toast, just update the UI)

Was this a major milestone (first save, onboarding complete)?
  → Celebratory state (animation, modal, or dedicated success screen)
```

**Toast guidelines**:
- Position: top-right (desktop) or bottom-center (mobile)
- Duration: 3s for info, 5s for success/warning, persistent for errors
- Message: verb + noun ("Product saved", "File deleted")
- Never auto-dismiss error toasts — user must acknowledge

---

### 3. Error State

**Purpose**: Tell the user what went wrong and what to do next.

Classify errors by source:

| Error Type | Example | UI Response |
|---|---|---|
| Validation error | Required field empty | Inline, below the field, with `aria-describedby` |
| Network error | No internet connection | Toast + retry button |
| Server error (5xx) | Internal server error | Error boundary or inline error with retry |
| Not found (404) | Resource deleted | Inline "no longer available" message |
| Auth error (401/403) | Session expired | Redirect to login with return URL |
| Rate limit (429) | Too many requests | Toast with "try again in X minutes" |

**Error message rules**:
- Never show raw error messages or stack traces to users
- Be specific: "Couldn't save your changes" > "Error"
- Offer a path forward: "Try again", "Go back", "Contact support"
- Preserve user's input — never clear a form on error

**Retry strategy**:
- Network errors: always offer retry
- Validation errors: no retry — fix the input
- Auth errors: redirect to login
- Server errors: offer retry + escalation path

---

### 4. Empty State

**Purpose**: Explain why nothing is showing and guide the user to act.

Classify empty states:

| Type | When | UI Response |
|---|---|---|
| First-time empty | User hasn't created anything yet | Illustration + CTA ("Create your first X") |
| Search empty | Query returned no results | "No results for '[query]'" + clear search option |
| Filter empty | Filters too narrow | "No items match your filters" + clear filters CTA |
| Error empty | Data failed to load | Same as error state — don't hide the failure |
| Awaiting state | Data loading is deferred | Skeleton (not empty state) |

**Empty state content**:
1. Icon or illustration (optional but helpful)
2. Headline: What's missing ("No products yet")
3. Supporting text: Why it's empty / what to expect
4. CTA: What to do next (primary action button)

---

## Step 1 — Inventory All Async Operations

List every async operation in the feature:

```
| Operation | Trigger | Loading | Success | Error | Empty |
|-----------|---------|---------|---------|-------|-------|
| Fetch product list | Page load | Skeleton (5 items) | Show list | Inline error + retry | "No products" + CTA |
| Add to cart | Button click | Button spinner | Toast "Added!" | Toast "Couldn't add" | — |
| Delete product | Delete button | Button spinner | Remove from list + toast | Toast + undo action | — |
| Search products | Input change | Subtle spinner | Update list | Inline error | "No results for X" |
```

## Step 2 — Design Each State

For each operation, write the exact copy and behavior:

```
## Operation: Fetch Product List

### Loading
- Skeleton: 5 ProductCard skeletons (same grid layout)
- Shimmer animation: left-to-right, 1.5s ease

### Success
- Render: ProductGrid with data
- Transition: Fade in over 200ms

### Error
- Component: InlineError
- Message: "Couldn't load products. Check your connection."
- Action: [Retry] button → re-fires the query
- Fallback: If retry fails 3 times → "Please refresh the page"

### Empty
- Icon: box-open
- Headline: "No products yet"
- Body: "Add your first product to get started."
- CTA: [Add Product] → opens AddProductModal
```

## Step 3 — Define Transition Behavior

State transitions should feel smooth, not jarring:

- **Loading → Success**: Fade in (200ms) or skeleton-to-content crossfade
- **Loading → Error**: Skeleton fades out, error fades in
- **Success → Error** (background refresh): Don't unmount success state — show toast overlay
- **Error → Retry Loading**: Clear error, show skeleton again

## Output Format

```
## UX / Feedback Design

### Async Operations Matrix

| Operation | Loading | Success | Error | Empty |
|-----------|---------|---------|-------|-------|
| [op] | [how] | [how] | [how] | [how] |

### State Details

#### [Operation Name]
- Loading: [description]
- Success: [description + copy]
- Error: [description + copy + recovery action]
- Empty: [description + copy + CTA]

### Toast Specifications
- Position: [location]
- Duration: [ms by type]
- Stack behavior: [newest on top / replace / queue]

### Error Copy Guidelines
- [Specific error messages for this feature]
```

## Anti-Patterns to Avoid

- **Silent failures**: If an action fails, always tell the user
- **Clearing form on error**: Never lose the user's input
- **Auto-dismissing errors**: Errors must be acknowledged
- **Generic messages**: "Something went wrong" tells the user nothing
- **Skeleton forever**: Set a max skeleton duration — if data never loads, show an error
- **Hiding empty state**: A truly empty list should never just show nothing
- **Loading on top of content**: Background refreshes should not replace visible content with a spinner