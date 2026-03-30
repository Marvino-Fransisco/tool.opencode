---
name: fe-request-analysis
description: Use this skill when the frontend agent needs to fully understand and decompose a user's feature request before designing. Triggers include: any design task, "I want a feature that…", "build me a…", "add X to the app", or any user prompt describing frontend functionality. Applies the layered thinking framework (Goal → Flow → Data → UI → Feedback → Perf → Reliability → A11y) and decomposes the request into a ranked list of concrete sub-problems. Always run after project-reader, pattern-detector, and doc-reader.
---

This skill teaches the agent to think deeply before designing — decomposing one vague request into a precise set of solvable problems.

## Goal

Transform a user's request into:
1. A clear **problem statement** (what actually needs to be built)
2. A set of **sub-problems** with solutions
3. A **priority ranking** so the design focuses on what matters most

## The Layered Thinking Framework

Apply all 8 layers to every request. Never skip a layer — even if you think it doesn't apply, stating "not applicable, because…" is valid and useful.

---

### Layer 1 — Goal
**Question**: What is the user *actually* trying to accomplish?

Not the feature they described — the underlying intent.

Ask:
- What problem does this solve for the end user?
- What does "success" look like from the user's perspective?
- Is there a simpler way to achieve this goal that the user hasn't considered?

Output: 1–2 sentence user goal statement.

---

### Layer 2 — Flow
**Question**: What are all the ways a user can move through this feature?

Map:
- **Happy path**: Step-by-step of the ideal interaction
- **Edge cases** (always include these):
  - [ ] API failure (network error, 500, timeout)
  - [ ] Empty state (no data returned, first-time user)
  - [ ] Slow network (request takes 3–10 seconds)
  - [ ] Invalid input (user enters bad data)
  - [ ] Permission denied (unauthenticated, unauthorized)
  - [ ] Concurrent actions (user clicks twice, navigates away mid-request)
  - [ ] Partial failure (some data loads, some doesn't)

Output: Happy path steps + checked edge case list.

---

### Layer 3 — Data
**Question**: Where does data come from and how does it move?

Ask:
- What API endpoints are needed? (cross-reference doc-reader output)
- What is the shape of the data?
- Where should state live? (local component / shared store / server cache)
- Does data need to be cached? For how long?
- What triggers a data refresh?
- Are there optimistic updates needed?

Output: Data source, state location decision, cache strategy.

---

### Layer 4 — UI
**Question**: What components are needed and how do they relate?

Ask:
- What is the top-level layout?
- What existing components from the design system can be reused?
- What new components need to be created?
- How does the layout respond to different screen sizes?
- What is the visual hierarchy? What draws the eye first?

Output: Component list with responsibilities.

---

### Layer 5 — Feedback
**Question**: How does the UI communicate system state to the user?

For every async operation, define:
- **Loading state**: What does the user see while waiting?
- **Success state**: How is success communicated? (toast, inline, redirect)
- **Error state**: How is the error shown? Is it recoverable?
- **Empty state**: What appears when there's no data?

Output: Feedback state matrix.

---

### Layer 6 — Performance
**Question**: What could make this feature slow, and how do we prevent it?

Ask:
- Will this component re-render too often? (unnecessary parent re-renders)
- Is the data payload large? (pagination, virtualization needed?)
- Are there network waterfalls? (parallel requests vs sequential)
- Will this block the main thread? (heavy computation → Web Worker?)
- Is code-splitting needed? (lazy load the route/component)

Output: List of performance risks and mitigations.

---

### Layer 7 — Reliability
**Question**: What can break in production, and how do we handle it?

Ask:
- What happens if the API never responds?
- What if the user's session expires mid-flow?
- What if data arrives in an unexpected shape?
- What if a third-party service (maps, payments, auth) is down?
- Are there race conditions? (search debounce, request cancellation)

Output: Failure modes + recovery strategies.

---

### Layer 8 — Accessibility
**Question**: Can everyone use this feature?

Check:
- Is every interactive element reachable by keyboard?
- Do all images/icons have meaningful alt text?
- Is color contrast sufficient? (WCAG AA minimum: 4.5:1 for text)
- Are dynamic updates announced to screen readers? (`aria-live`)
- Does the feature work at 200% zoom?
- Are error messages associated with their form fields? (`aria-describedby`)

Output: A11y checklist for this specific feature.

---

## Decomposition Process

After the 8 layers, list all problems discovered:

```
## Sub-Problems (ranked by impact)

1. [Highest impact / most complex problem]
2. [Second problem]
3. ...
```

For each sub-problem, answer:
- **What** is the problem exactly?
- **When** does it occur?
- **Why** does it matter?
- **How** will we solve it?

## Output Format

```
## Request Analysis

### Interpreted Goal
[What the user actually wants, in plain English]

### Problem Statement
[Clear summary: what needs to be built, what constraints apply]

---

### Layer Analysis

| Layer | Finding | Action Needed |
|-------|---------|---------------|
| Goal | [finding] | [action] |
| Flow | [finding] | [action] |
| Data | [finding] | [action] |
| UI | [finding] | [action] |
| Feedback | [finding] | [action] |
| Performance | [finding] | [action] |
| Reliability | [finding] | [action] |
| Accessibility | [finding] | [action] |

---

### Sub-Problems (ranked)
1. [Problem] → [Proposed solution]
2. [Problem] → [Proposed solution]
...

### Assumptions Made
- [List anything assumed that wasn't stated — these should be validated]

### Questions to Clarify (if any)
- [Only list if blocking — don't ask questions that can be reasonably assumed]
```

## Anti-Patterns to Avoid

- **Over-scoping**: Don't solve problems the user didn't ask for
- **Under-scoping**: Don't ignore edge cases because they seem unlikely
- **Jargon dumping**: Analysis should be readable by the user, not just engineers
- **Analysis paralysis**: If something is ambiguous, make a reasonable assumption and flag it — don't block on it