---
name: fe-markdown-format
description: Use this skill when the frontend agent needs to compile all design outputs into the final design document. Triggers include: "create the design file", "write the design doc", or after all other design skills have been run and the agent is ready to produce the final markdown output. This skill takes all upstream outputs (request-analyser, component-designer, state-designer, ux-feedback-designer, perf-advisor, a11y-checker, edge-case-generator, tradeoff-advisor) and assembles them into a single, clean markdown file following the exact template. Always run LAST.
---

This skill guides the agent to compile all design thinking into a single, well-structured markdown file.

## Goal

Produce one markdown file that:
- Follows the exact template structure
- Is complete — no empty or placeholder sections
- Is readable by both engineers and non-engineers
- Serves as the single source of truth for the feature design

---

## Pre-flight Checklist

Before writing the file, verify all inputs are available:

- [ ] **request-analyser** output → fills: User Goal, Problem Statement, Core Flows
- [ ] **component-designer** output → fills: UI / Component Structure
- [ ] **state-designer** output → fills: Data & State
- [ ] **ux-feedback-designer** output → fills: UX / Feedback
- [ ] **perf-advisor** output → fills: Performance Considerations
- [ ] **a11y-checker** output → fills: Accessibility
- [ ] **edge-case-generator** output → fills: Edge Cases, Test cases in Solutions
- [ ] **tradeoff-advisor** output → fills: Tradeoffs / Decisions
- [ ] **diagram-generator** output (if run) → fills: High Level Diagrams

If any input is missing, run the corresponding skill first. Do not leave sections blank with "TBD".

---

## File Naming Convention

```
[feature-name]-design.md
```

Examples:
- `product-search-design.md`
- `user-onboarding-design.md`
- `checkout-flow-design.md`
- `notification-center-design.md`

Use kebab-case. Be specific — `feature-design.md` is not acceptable.

---

## The Template

Fill every section. If a section truly doesn't apply, write one sentence explaining why (e.g., "No performance concerns — this component renders a single static value and has no async operations."). Never leave a section empty.

```markdown
# [Feature Name] — Frontend Design

## User Prompt
> [Paste the exact original user request here, unchanged]

## Problem Statement
[2–4 sentences. What needs to be built, what constraints apply, what success looks like.]

---

## User Goal
[1–2 sentences. What the user is actually trying to achieve — not the feature, the intent.]

## Core Flows

### Happy Path
1. [Step 1]
2. [Step 2]
3. [Step 3]
...

### Edge Cases
- [ ] API failure → [behavior]
- [ ] Empty data → [behavior]
- [ ] Slow network → [behavior]
- [ ] Invalid input → [behavior]
- [ ] Session expired → [behavior]
- [ ] [Feature-specific edge case] → [behavior]

---

## Data & State

### State Inventory
| State | Type | Location | Reason |
|-------|------|---------|--------|
| [name] | [UI/Server/Global] | [where] | [why] |

### Server State Hooks
\`\`\`ts
// [hook name]
[hook skeleton]
\`\`\`

### Store Design (if applicable)
\`\`\`ts
// [store name]
[store interface]
\`\`\`

### Cache Strategy
- Stale time: [value]
- Refetch triggers: [list]
- Optimistic updates: [yes/no + detail]

---

## UI / Component Structure

### Component Tree
\`\`\`
[ComponentName] (Page)
  ├── [ChildA] (Feature)
  │     └── [ChildB] (UI)
  └── [ChildC] (Skeleton)
\`\`\`

### Component Responsibilities
| Component | Type | Responsibility | Data Source |
|-----------|------|---------------|-------------|
| [Name] | [type] | [what it does] | [source] |

### Props Interfaces
\`\`\`ts
interface [ComponentName]Props {
  [prop]: [type]; // [why]
}
\`\`\`

### Reusability
| Component | Status | Notes |
|-----------|--------|-------|
| [Name] | [Reuse/New shared/New local] | [detail] |

---

## UX / Feedback

### Async Operations Matrix
| Operation | Loading | Success | Error | Empty |
|-----------|---------|---------|-------|-------|
| [op] | [how] | [how] | [how] | [how] |

### State Details

#### [Operation Name]
- **Loading**: [description]
- **Success**: [copy + behavior]
- **Error**: [copy + recovery action]
- **Empty**: [copy + CTA]

---

## Performance Considerations

### Render
| Component | Risk | Mitigation |
|-----------|------|------------|
| [Name] | [risk] | [fix] |

### Network
| Operation | Risk | Mitigation |
|-----------|------|------------|
| [op] | [risk] | [fix] |

### Optimization Checklist
- [ ] [specific optimization]
- [ ] [specific optimization]

---

## Accessibility

### Keyboard Navigation
- [ ] Tab order is logical
- [ ] [Component] supports Arrow/Enter/Escape keys
- [ ] Focus trap in [modal/drawer]
- [ ] Focus returns to [trigger] when [modal] closes

### Screen Reader
- [ ] Semantic HTML throughout
- [ ] Icon-only buttons have aria-label
- [ ] Dynamic content uses aria-live
- [ ] Form errors linked via aria-describedby

### Visual
- [ ] All text meets 4.5:1 contrast
- [ ] Color not used as sole indicator
- [ ] Works at 200% zoom

---

## Tradeoffs / Decisions

| Decision | Chosen | Reason | Tradeoff |
|----------|--------|--------|---------|
| [topic] | [choice] | [why] | [cost] |

### [Decision Title]
**Context**: [why this decision was needed]
**Chosen**: [what was decided]
**Why**: [specific reasons]
**Tradeoffs**: [what's accepted]
**Revisit when**: [conditions]

---

## High Level Diagrams

### Component Flow
[Mermaid diagram or ASCII]

### Data Flow
[Mermaid diagram or ASCII]

### State Machine (if applicable)
[Mermaid diagram or ASCII]

---

## Solutions (Sequential Implementation Order)

> Implement in this order. Each solution is self-contained and testable.

- [1] [Problem name] → [Solution summary]
- [2] [Problem name] → [Solution summary]
- [3] [Problem name] → [Solution summary]
...

---

## 1. [Problem Name]

### Problem
[What specifically is the problem? Why does it need to be solved?]

### Solution
[How is it solved? What does the implementation look like?]

### Steps
- [ ] [Concrete implementation step]
- [ ] [Concrete implementation step]
- [ ] [Concrete implementation step]

### Tests
- [ ] [Test: describe the scenario and expected outcome]
- [ ] [Test: describe the scenario and expected outcome]

### Edge Cases Covered
- [ ] [Edge case and how this solution handles it]
- [ ] [Edge case and how this solution handles it]

---

## 2. [Problem Name]

[... repeat structure ...]
```

---

## Writing Quality Rules

**Problem Statement**: Must be concrete. Bad: "We need to build a product page." Good: "We need a paginated product listing page that supports filtering by category and price, fetches from GET /api/products, and handles empty and error states."

**Solutions list**: Must be in implementation order. A junior developer should be able to implement them one by one without needing to ask questions.

**Steps**: Must be concrete and actionable. Bad: "Build the component." Good: "Create `src/features/products/ProductGrid.tsx` with a `ProductGridProps` interface containing `products: Product[]` and `isLoading: boolean`."

**Tests**: Must describe observable behavior. Bad: "Test the component." Good: "Render with `products=[]` → empty state component appears with 'No products yet' headline and 'Add Product' CTA button."

---

## File Output

Save to: `[feature-name]-fe-design.md`

The file should be self-contained. Someone who wasn't part of the design discussion should be able to read it and understand:
- What is being built and why
- How to implement it
- What can go wrong and how it's handled
- Why the key decisions were made