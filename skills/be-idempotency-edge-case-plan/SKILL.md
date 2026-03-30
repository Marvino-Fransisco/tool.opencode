---
name: be-idempotency-edge-case-plan
description: Use this skill when the user needs to systematically identify edge cases and design idempotency for a backend feature. Triggers include: designing a write operation that could be retried, planning for duplicate requests, handling race conditions, or stress-testing a design against failure scenarios. Also use when the user asks "what could go wrong", "how do I handle duplicates", "make this retry-safe", or before finalizing any feature design.
---

This skill guides the systematic surfacing of edge cases and the design of idempotency guards for backend features.

The user provides a feature or endpoint design. The goal is to find every way it can go wrong and design concrete defenses before implementation begins.

## Edge Case Framework

Apply each category to the feature and ask: "What happens if this occurs?"

### Input Edge Cases
- **Empty / null / missing fields** — required field not sent, optional field is null
- **Wrong types** — string where int expected, array where object expected
- **Out of range values** — negative quantity, price of $0, date in the past, date 100 years in the future
- **Oversized payloads** — string that's 1MB, array with 10,000 items
- **Special characters** — SQL injection attempt, XSS payload, unicode edge cases (emoji, RTL text, null bytes)
- **Boundary values** — exactly at the limit (max length, max count)
- **Duplicate submission** — same request sent twice (user double-clicked, network retry)

### State Edge Cases
- **Resource doesn't exist** — GET/PATCH/DELETE on a non-existent ID
- **Resource in wrong state** — trying to cancel an already-delivered order
- **Resource owned by someone else** — IDOR attempt
- **Concurrent modification** — two requests modify the same resource simultaneously
- **Already processed** — idempotent operation sent again after success

### Dependency Edge Cases
- **DB unavailable** — query fails mid-transaction
- **Partial transaction** — first DB write succeeds, second fails
- **External service down** — payment gateway, email provider, third-party API
- **External service slow** — timeout after 30s, partial data returned
- **External service returns unexpected data** — missing fields, changed schema

### Business Logic Edge Cases
- **Insufficient funds / quota** — user tries to exceed their limit
- **Expired resource** — token expired, coupon expired, session timed out
- **Permission changed mid-flow** — user's role was changed between login and action
- **Cascade effects** — deleting a resource that other resources depend on

### Infrastructure Edge Cases
- **Request timeout** — client disconnects before server responds
- **Server restart mid-request** — process killed during a write operation
- **Clock skew** — two servers have different system times
- **Retry storm** — all clients retry simultaneously after an outage

## Idempotency Design

### When is idempotency required?
- Any **write operation** that could be retried by the client or by internal retry logic
- Any operation that **charges money**, **sends a notification**, or **creates a resource**
- Any **background job** that could be triggered more than once

### Idempotency Key Pattern
1. Client generates a unique key per logical operation (UUID v4)
2. Client sends it as a header: `Idempotency-Key: <uuid>`
3. Server checks if it has seen this key before:
   - **Not seen**: process the request, store the result, return the result
   - **In progress**: return 409 Conflict (or 202 Accepted if async)
   - **Already processed**: return the stored result immediately (same status code as original)
4. Store idempotency records with a TTL (24hr–7 days depending on use case)

### Idempotency Storage
```
idempotency_keys table:
- key (unique, indexed)
- request_hash (hash of method + path + body — to detect same key, different request)
- response_status
- response_body
- created_at
- expires_at
```

### Natural Idempotency
Some operations are naturally idempotent if designed correctly:
- **Upsert** (`INSERT ... ON CONFLICT DO UPDATE`) instead of insert-then-update
- **Set state explicitly** (`UPDATE orders SET status = 'cancelled'`) instead of toggling
- **Check before act** (`IF status != 'cancelled' THEN cancel`) with a DB-level lock

### Race Condition Guards
For concurrent modification:
- **Optimistic locking**: include a `version` or `updated_at` in the update request; reject if it doesn't match current DB value
- **Pessimistic locking**: `SELECT ... FOR UPDATE` to lock the row before reading and writing
- **DB constraints**: unique constraints, check constraints as the last line of defense
- **Atomic operations**: use DB-level atomic increments (`UPDATE SET count = count + 1`) instead of read-modify-write in application code

## Output Format

### Edge Case Inventory
For each edge case found:
| Category | Edge Case | Current behavior | Required behavior | Guard needed |
|---|---|---|---|---|
| Input | Quantity is 0 | Not validated | Return 400 | Validation rule |
| State | Order already cancelled | Would cancel again | Return 409 | State check |
| Concurrency | Two requests ship same order | Both succeed | One succeeds, one 409 | Pessimistic lock |

### Idempotency Requirements
- Which endpoints need idempotency keys?
- Storage design (table schema or cache key pattern)
- TTL recommendation
- Behavior on duplicate key detection

### Race Condition Guards
- Which operations have concurrent modification risk?
- Locking strategy (optimistic vs pessimistic) for each
- DB constraints to add as safety net

### Missing Validations
List every input validation that should be added and at which layer.

### Open Questions
Ambiguities that need product or business clarification before the edge cases can be fully resolved.