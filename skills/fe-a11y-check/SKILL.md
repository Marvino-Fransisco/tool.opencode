---
name: fe-a11y-check
description: Use this skill when the frontend agent needs to ensure a feature design is accessible. Triggers include: any UI design task, forms, modals, dialogs, menus, tooltips, dynamic content, notifications, or whenever the agent is reviewing a component tree. Always run after component-designer. Output fills the "Accessibility" section of the design document. WCAG 2.1 AA is the minimum standard.
---

This skill guides the agent to design accessible UIs from the start, not as an afterthought.

## Goal

Produce an **Accessibility Checklist** specific to the feature being designed, covering:
1. Keyboard navigation
2. Screen reader compatibility
3. Visual accessibility
4. Semantic HTML
5. Focus management

---

## Layer 1 — Keyboard Navigation

Every interactive element must be reachable and operable by keyboard alone.

### Tab Order
- Tab order must follow the visual reading order (left-to-right, top-to-bottom)
- Use `tabIndex="0"` to add non-interactive elements to tab order only when necessary
- Never use `tabIndex` > 0 — it breaks natural tab order
- Skip links: add a "Skip to main content" link as the first focusable element on every page

### Keyboard Shortcuts by Component

| Component | Expected Keys |
|---|---|
| Button | `Enter`, `Space` to activate |
| Link | `Enter` to navigate |
| Checkbox | `Space` to toggle |
| Radio group | `Arrow` keys to move between options |
| Select / Dropdown | `Enter` to open, `Arrow` keys to navigate, `Enter`/`Space` to select, `Escape` to close |
| Modal/Dialog | `Escape` to close, focus trapped inside while open |
| Tabs | `Arrow` keys to move between tabs, `Enter` to activate |
| Accordion | `Enter`/`Space` to expand/collapse |
| Date picker | Full keyboard grid navigation |
| Combobox / Autocomplete | `Arrow` keys for list, `Enter` to select, `Escape` to dismiss |

### Focus Trap

Required in:
- Modals and dialogs (focus must not escape to background)
- Drawers / side panels
- Dropdown menus (while open)
- Toast notifications (if they have actions)

Implementation: Use `focus-trap-react` or the browser-native `inert` attribute on background content.

### Focus Visible

- Never remove focus outlines: `outline: none` is only acceptable if you replace it with an equally visible custom focus style
- Focus style minimum: 2px solid offset outline with 3:1 contrast ratio against adjacent colors
- Test: Tab through every interactive element — the focused element must always be obvious

---

## Layer 2 — Screen Reader Compatibility

### Semantic HTML

Prefer native HTML over custom implementations:

| Use this | Not this |
|---|---|
| `<button>` | `<div onClick>` |
| `<a href>` | `<span onClick>` |
| `<nav>` | `<div class="nav">` |
| `<main>` | `<div id="main">` |
| `<h1>–<h6>` | `<p class="title">` |
| `<ul><li>` | `<div><div>` for lists |
| `<table>` | Div grid for tabular data |
| `<form>` | Div with inputs |

### ARIA — Use Sparingly

ARIA should supplement semantic HTML, not replace it.

Required ARIA attributes by pattern:

| Pattern | Required ARIA |
|---|---|
| Icon-only button | `aria-label="[action]"` |
| Toggle button | `aria-pressed="true/false"` |
| Expanded section | `aria-expanded="true/false"` |
| Loading state | `aria-busy="true"` on the container |
| Error message | `role="alert"` or `aria-live="assertive"` |
| Status update | `aria-live="polite"` |
| Modal | `role="dialog"`, `aria-modal="true"`, `aria-labelledby="[title-id]"` |
| Progress | `role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax` |
| Required field | `aria-required="true"` |
| Invalid field | `aria-invalid="true"`, `aria-describedby="[error-id]"` |

### Dynamic Content Announcements

When content updates without a page reload:

- **Success/error notifications**: `role="alert"` (assertive) for errors, `aria-live="polite"` for success
- **Loading complete**: Announce result count ("Showing 24 products")
- **Page navigation in SPA**: Update `document.title` and announce the new page to screen readers
- **Toast messages**: Wrap toast container in `aria-live="polite"`

### Form Accessibility

Every form must have:
- `<label>` for every input, associated via `for`/`htmlFor` or wrapping
- Error messages linked to inputs via `aria-describedby`
- Required fields marked with `aria-required` AND a visible indicator
- Submit button with descriptive text ("Save product", not just "Submit")
- Field groupings using `<fieldset>` + `<legend>` for related fields (radio groups, checkboxes)

```tsx
// Correct
<div>
  <label htmlFor="email">Email address</label>
  <input
    id="email"
    type="email"
    aria-required="true"
    aria-invalid={!!errors.email}
    aria-describedby={errors.email ? "email-error" : undefined}
  />
  {errors.email && (
    <span id="email-error" role="alert">{errors.email}</span>
  )}
</div>
```

---

## Layer 3 — Visual Accessibility

### Color Contrast (WCAG 2.1 AA)

| Text Type | Minimum Ratio |
|---|---|
| Normal text (< 18pt) | 4.5:1 |
| Large text (≥ 18pt or 14pt bold) | 3:1 |
| UI components / borders | 3:1 |
| Placeholder text | 4.5:1 |
| Disabled elements | No requirement (but avoid invisible) |

Tools: browser DevTools color picker, axe, Colour Contrast Analyser

### Color Is Not the Only Indicator

Never rely on color alone to convey meaning:

- Error fields: red border AND an error icon AND text message
- Required fields: asterisk AND aria-required AND label text
- Status badges: colored AND text label ("Active", "Inactive")
- Charts: colored lines AND data labels or patterns

### Text Sizing

- Minimum body text: 16px (1rem)
- Everything must work at 200% zoom (browser zoom, not just CSS zoom)
- Don't use `px` for font sizes that should scale — use `rem`

---

## Layer 4 — Focus Management

### After Async Operations

| Scenario | Focus Should Go To |
|---|---|
| Modal opens | First focusable element inside modal |
| Modal closes | Element that triggered the modal |
| Form submitted (success) | Success message or next logical element |
| Form submitted (error) | First error field |
| Item deleted from list | Next item, or previous item if last |
| Page navigation | Page `<h1>` or `<main>` |

---

## Output Format

```
## Accessibility Checklist

### Keyboard Navigation
- [ ] Tab order follows visual reading order
- [ ] [specific component] keyboard shortcuts implemented (Arrow, Enter, Escape)
- [ ] Focus trap applied to [modal/drawer name]
- [ ] Focus visible on all interactive elements
- [ ] Skip-to-content link present

### Screen Reader
- [ ] Semantic HTML used throughout (no div-soup)
- [ ] Icon-only buttons have aria-label
- [ ] [Modal name] has role="dialog", aria-modal, aria-labelledby
- [ ] Dynamic content (search results, notifications) announced via aria-live
- [ ] Form errors linked via aria-describedby
- [ ] Loading states communicate aria-busy

### Visual
- [ ] All text meets 4.5:1 contrast ratio
- [ ] UI components meet 3:1 contrast
- [ ] Errors communicated with icon + text, not color alone
- [ ] UI works at 200% browser zoom

### Focus Management
- [ ] Modal close → focus returns to trigger
- [ ] Form error → focus moves to first error field
- [ ] [other specific scenario] → focus goes to [target]

### Semantic Structure
- [ ] Page has single <h1>
- [ ] Heading hierarchy is logical (h1 → h2 → h3)
- [ ] Navigation wrapped in <nav>
- [ ] Main content in <main>
- [ ] Lists use <ul>/<ol> + <li>
```

## Testing

Manual testing checklist (do this before shipping):
1. Tab through the entire feature — every interactive element must be reachable
2. Use it with screen reader (NVDA/Windows, VoiceOver/Mac)
3. Zoom to 200% — nothing should break or overflow
4. Disable CSS — content should still be readable and logical
5. Run axe DevTools or Lighthouse Accessibility audit — aim for 0 violations