---
name: fe-tradeoff-advice
description: Use this skill when the frontend agent needs to document design decisions and their rationale. Triggers include: any point in the design where two or more valid approaches exist, "why did you choose X over Y", "what are the tradeoffs", "alternatives considered", or after the design is substantially complete and needs its decisions justified. Always run as a final pass before markdown-formatter. Output fills the "Tradeoffs / Decisions" section of the design document.
---

This skill guides the agent to think critically about its own design choices, document the reasoning, and surface risks — so that future engineers understand *why*, not just *what*.

## Goal

For every non-obvious design decision, produce:
1. **The decision made**
2. **The alternatives considered**
3. **Why this option was chosen**
4. **What is traded off**
5. **When this decision should be revisited**

---

## When a Tradeoff Document is Required

Document a decision when:
- Two or more valid approaches existed
- The choice has meaningful impact on: performance, maintainability, UX, scalability, or DX
- A future engineer would reasonably ask "why didn't they just…?"
- The choice deviates from the existing project pattern (requires extra justification)

---

## Decision Categories

### State Management Decisions

Common tradeoffs to evaluate:

| Decision | Option A | Option B | Key Tradeoff |
|---|---|---|---|
| Where state lives | Local useState | Global store | Simplicity vs shareability |
| Server state | Manual fetch + useState | React Query | Code volume vs caching/devex |
| URL vs store | Store (in-memory) | URL search params | Performance vs shareability/bookmarking |
| Optimistic updates | Optimistic (instant UI) | Pessimistic (wait for server) | Speed vs correctness |

### Component Architecture Decisions

| Decision | Option A | Option B | Key Tradeoff |
|---|---|---|---|
| Composition | Flat, many components | Nested, fewer components | Reusability vs simplicity |
| Feature vs shared | Feature-local component | Shared component | Isolation vs DRY |
| Context vs prop drilling | Context API | Explicit props | Implicitness vs verbosity |
| Controlled vs uncontrolled | Controlled input | Uncontrolled + ref | Full control vs simplicity |

### UX Decisions

| Decision | Option A | Option B | Key Tradeoff |
|---|---|---|---|
| Feedback pattern | Toast notification | Inline success state | Transience vs persistence |
| Loading pattern | Skeleton | Spinner | Layout stability vs simplicity |
| Error recovery | Retry button | Full page reload | Granularity vs simplicity |
| Pagination | Infinite scroll | Page numbers | Engagement vs navigability |
| Validation timing | On blur | On change | Feedback speed vs interruption |

### Performance Decisions

| Decision | Option A | Option B | Key Tradeoff |
|---|---|---|---|
| Rendering | Client-side rendering | SSR/SSG | Interactivity vs initial load |
| Data freshness | Poll every 30s | WebSocket | Simplicity vs real-time |
| Image loading | Eager | Lazy | First image speed vs bandwidth |
| Code splitting | Split at route level | Split at component level | Simplicity vs granularity |

---

## The Decision Template

For each significant decision, fill this out:

```
### Decision: [Short title]

**Context**: [Why was a decision needed here? What constraint or requirement triggered it?]

**Options Considered**:
1. [Option A] — [brief description]
2. [Option B] — [brief description]
3. [Option C] — [brief description, if applicable]

**Decision**: [Option chosen]

**Why**:
- [Primary reason — the most important factor]
- [Secondary reason]
- [Pattern alignment — "consistent with how X is already done in the project"]

**Tradeoffs Accepted**:
- [What we're giving up or accepting as a consequence]
- [What becomes harder because of this choice]

**Revisit When**:
- [Condition that would make us reconsider — e.g., "if this component is reused in more than 3 places", "if real-time requirements emerge"]
```

---

## Example Decisions

### Example 1: State location for search filters

```
### Decision: Store search filters in URL params, not Zustand store

Context: The product list page has filters (category, price range, sort). Multiple components
read and write filter state.

Options Considered:
1. Zustand store — dedicated filterStore atom
2. URL search params — ?category=shoes&sort=price_asc
3. Local state lifted to page component

Decision: URL search params

Why:
- Users can share/bookmark filtered views (high user value)
- Browser back/forward navigation works as expected
- No store hydration needed on page load
- Consistent with how the existing /search page works (pattern alignment)

Tradeoffs Accepted:
- Slightly more verbose code (useSearchParams + serialization)
- Filter state is visible in the URL (acceptable — not sensitive)
- URL length limit is technically possible with many filter combinations (edge case, not expected)

Revisit When:
- Filters become sensitive/private (then use session storage)
- Filter state needs to be read by non-URL components (then add store as mirror)
```

### Example 2: Loading pattern

```
### Decision: Skeleton loading over spinner for product grid

Context: Product grid fetches 12–24 products on page load. Need a loading state.

Options Considered:
1. Centered spinner
2. Skeleton cards (12 placeholders matching ProductCard shape)
3. Loading progress bar at top of page

Decision: Skeleton cards

Why:
- Prevents layout shift when real content loads (CLS score)
- Sets user expectations about content shape and count
- Perceived performance is better — brain interprets shapes as "almost ready"

Tradeoffs Accepted:
- More code to maintain (skeleton must be updated if ProductCard layout changes)
- Slightly more complex than a spinner

Revisit When:
- ProductCard layout changes significantly (update skeleton in same PR)
```

---

## Final Pass Checklist

Before handing off to markdown-formatter, verify:

- [ ] Every non-obvious architectural decision has a documented rationale
- [ ] Every place the design deviates from the existing project pattern is explained
- [ ] Alternatives considered are listed (not just the chosen approach)
- [ ] "Revisit when" conditions are defined for at least the most significant decisions
- [ ] No decision is justified with "because it's best practice" alone — be specific

---

## Output Format

```
## Tradeoffs & Decisions

| Decision | Chosen Approach | Key Reason | Tradeoff Accepted |
|----------|----------------|-----------|------------------|
| [topic] | [choice] | [why] | [what we give up] |

---

[Full decision blocks for the 3–5 most significant choices]

### Decision: [Title]
Context: ...
Options: ...
Decision: ...
Why: ...
Tradeoffs: ...
Revisit When: ...
```

## Anti-Patterns to Avoid

- **Post-hoc rationalization**: Don't start with the conclusion and build the argument — evaluate genuinely
- **Ignoring existing patterns**: "I prefer X" is not enough justification to break conventions
- **Missing alternatives**: If only one option is listed, the tradeoff wasn't analyzed
- **Vague justifications**: "Better DX" or "cleaner code" without specifics is not useful documentation
- **Never revisiting**: Good decisions become bad decisions as requirements change — set revisit conditions