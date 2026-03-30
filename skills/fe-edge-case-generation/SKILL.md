---
name: fe-edge-case-generation
description: Use this skill when the frontend agent needs to enumerate failure modes and edge cases for a feature. Triggers include: any feature with async operations, user input, navigation, authentication, or real-time data. Also triggers for "what can go wrong", "test cases", "edge cases", "reliability". Always run after request-analyser and state-designer. Output fills the "Core Flows - Edge Cases" section and "Test" subsections of the design document.
---

This skill guides the agent to systematically enumerate every way a feature can fail or behave unexpectedly — and define the correct response for each.

## Goal

Produce:
1. A **complete edge case register** for the feature
2. The **correct behavior** for each case
3. **Test cases** that verify the behavior

---

## The 8 Categories of Edge Cases

Apply all 8 categories to every feature. Skip only if genuinely irrelevant (state why).

---

### Category 1 — Network Failures

| Case | User Sees | System Does |
|---|---|---|
| Complete network loss | Error + retry button | Catch fetch error, show inline error |
| Request timeout (> 10s) | "Taking longer than expected" + retry | AbortController with timeout |
| Intermittent failure (flaky network) | Spinner → retry automatically 1–2x | Retry logic with backoff |
| Server error (500) | "Something went wrong on our end" | Log to monitoring, show user-friendly error |
| Service unavailable (503) | "Service is temporarily down" | Show maintenance message if header present |
| Slow response (3–8s) | Loading skeleton stays visible | Skeleton stays, no timeout error yet |

Questions to ask:
- Does the feature need offline support? (PWA)
- Is there a retry strategy? (immediate / exponential backoff / manual)
- Are failed mutations queued for retry when connection restores?

---

### Category 2 — Empty & Null Data

| Case | User Sees | System Does |
|---|---|---|
| API returns empty array `[]` | Empty state with CTA | Render empty state component |
| API returns `null` for optional field | Graceful fallback (placeholder, "—") | Null coalescing: `value ?? '—'` |
| API returns partial data (some fields missing) | Renders without missing fields | Optional chaining: `data?.field` |
| User hasn't set up their account yet | Onboarding empty state | Check `isFirstTime` flag from API |
| No results match search/filter | "No results" + clear filter CTA | Differentiate from "never had data" |

Questions to ask:
- What does the API return for empty vs error? (they must be distinguishable)
- Are there any required fields that could realistically be null?
- Does empty state differ for first-time users vs users who deleted everything?

---

### Category 3 — Invalid or Unexpected Input

| Case | User Sees | System Does |
|---|---|---|
| Required field left empty | Inline error on field | Block submission, focus first error |
| Input exceeds max length | Character count + error | `maxLength` attribute + server validation |
| Wrong format (email, URL, phone) | Format hint + error | Regex validation client-side |
| XSS attempt in text input | Input rendered as plain text | Sanitize on render — never `dangerouslySetInnerHTML` with user input |
| Negative numbers where positive expected | Range error message | `min` attribute + server validation |
| File upload wrong type/size | "File must be JPG/PNG under 5MB" | Accept attribute + size check before upload |
| Paste of extremely long text | Truncated or error | maxLength + graceful handling |

Questions to ask:
- Is all user input validated client-side AND server-side?
- Are validation error messages specific and actionable?
- Is user input ever rendered as HTML? If yes, is it sanitized?

---

### Category 4 — Race Conditions & Concurrency

| Case | User Sees | System Does |
|---|---|---|
| User clicks submit twice | Only one submission fires | Disable button on first click |
| User types fast in search | Results match the latest query | Cancel previous request with AbortController |
| User navigates away during async operation | No error, no memory leak | Cancel pending requests on unmount |
| Two users edit same resource simultaneously | Conflict notification | Optimistic lock (ETag) or last-write-wins with notification |
| Stale data shown after background refresh | Data updates smoothly | React Query invalidation, no flash |
| Component unmounts before fetch completes | No `setState on unmounted component` warning | Cleanup in useEffect return or AbortController |

Questions to ask:
- Are search/filter inputs debounced?
- Is the submit button disabled after first click?
- Are in-flight requests cancelled when the user navigates away?

---

### Category 5 — Authentication & Authorization

| Case | User Sees | System Does |
|---|---|---|
| Session expired mid-flow | "Session expired, please log in" + redirect | 401 interceptor → clear auth → redirect with return URL |
| User doesn't have permission | "You don't have access to this" | Check permissions before rendering, hide actions user can't take |
| Token refresh fails | Logged out gracefully | Catch refresh failure, redirect to login |
| Multiple tabs, logout in one | Other tabs redirect to login | Listen for storage event or BroadcastChannel |
| Deep link to protected page while logged out | Login page → redirect back to original URL | Return URL preserved in query param |
| Admin-only UI shown to regular user | Feature hidden or access denied page | Role check both client-side (UI) and server-side (API) |

Questions to ask:
- Are there role-based features in this component?
- What happens if the session expires in the middle of a multi-step form?
- Is the return URL preserved across login redirect?

---

### Category 6 — Performance Edge Cases

| Case | User Sees | System Does |
|---|---|---|
| 1000+ items in list | List still scrolls smoothly | Virtualization |
| Rapid filter/sort changes | No lag, correct results | Debounce + cancel previous request |
| Very large file upload | Progress indicator | Chunked upload + progress event |
| Low-end device | Acceptable performance | No heavy animations on `prefers-reduced-motion`, lazy images |
| Page left open for hours (stale data) | Fresh data on re-focus | `refetchOnWindowFocus: true` in React Query |

---

### Category 7 — Browser & Environment

| Case | User Sees | System Does |
|---|---|---|
| JavaScript disabled | Meaningful fallback or error | Progressive enhancement or clear "JS required" message |
| Old browser missing feature | Graceful degradation or polyfill | Check caniuse.com, add polyfills |
| Mobile viewport | Fully usable touch interface | Responsive design, touch targets ≥ 44px |
| Printed page | Readable print layout | `@media print` CSS |
| Slow connection (3G) | Skeletons, not blank | Skeleton loading, lazy images |
| Dark mode | Correct colors | CSS `prefers-color-scheme` or theme toggle |
| High contrast mode | Readable | Test with Windows High Contrast mode |

---

### Category 8 — Data Integrity

| Case | User Sees | System Does |
|---|---|---|
| Unsaved changes + navigation away | "You have unsaved changes" dialog | `beforeunload` event + router guard |
| Form partially filled + page refresh | Reasonable — data may be lost | Optional: localStorage auto-save draft |
| Duplicate submission | Error or idempotent handling | Idempotency key from server or client-generated UUID |
| Deleted resource still in client cache | "This item no longer exists" | Invalidate cache on 404, show error state |
| Concurrent edit conflict | Merge conflict notification | ETag or versioning |

---

## Output Format

```
## Edge Case Register

### Category 1: Network
| Case | Behavior | Covered By |
|------|---------|------------|
| Network loss | Error + retry | catch block in useProducts |
| Timeout > 10s | "Taking longer…" | AbortController 10s timeout |

[... repeat for all relevant categories ...]

### Test Cases

#### [Feature/Component Name]

| # | Test | Expected | Edge Case Category |
|---|------|---------|-------------------|
| 1 | Render with empty products array | Show empty state with "Add product" CTA | Empty data |
| 2 | API returns 500 | Show error message + retry button | Network failure |
| 3 | Click submit twice rapidly | Only one request fires | Race condition |
| 4 | Session expires during form fill | Redirect to login with return URL | Auth |
| 5 | Type 500 chars in name field | Truncated at maxLength, error shown | Invalid input |

### Prioritized Risk List
1. [Highest likelihood + impact risk]
2. [Second risk]
...
```

## Anti-Patterns to Avoid

- **Happy-path-only testing**: "It works when everything goes right" is not enough
- **Generic error handling**: Every error type deserves a specific, actionable response
- **Missing loading guards**: Every async operation can fail — handle it
- **Ignoring concurrent users**: Single-user testing misses race conditions
- **Assuming the API is reliable**: Networks fail, servers restart, rate limits hit