---
name: be-markdown-format
description: Use this skill when the backend agent needs to compile all design outputs into the final design document. Triggers include: "create the design file", "write the design doc", or after all other design skills have been run and the agent is ready to produce the final markdown output. This skill takes all upstream outputs (request-analyser, be-api-contract-design, be-data-schema-design, be-auth-authz-design, be-async-queue-plan, be-query-optimization, be-idempotency-edge-case-plan, be-observability-plan, be-dependency-risk-analysis, be-pattern-read, system-flow-diagram, tradeoff-advisor) and assembles them into a single, clean markdown file following the exact template. Always run LAST.
---

This skill guides the agent to compile all backend design thinking into a single, well-structured markdown file.

## Goal

Produce one markdown file that:
- Follows the exact template structure
- Is complete — no empty or placeholder sections
- Is readable by both engineers and non-engineers
- Serves as the single source of truth for the backend feature design

---

## Pre-flight Checklist

Before writing the file, verify all inputs are available:

- [ ] **request-analyser** output → fills: User Goal, Problem Statement, Core Flows
- [ ] **be-api-contract-design** output → fills: API Design
- [ ] **be-data-schema-design** output → fills: Data & Storage
- [ ] **be-auth-authz-design** output → fills: Security
- [ ] **be-async-queue-plan** output → fills: Async / Queue Design (if applicable)
- [ ] **be-query-optimization** output → fills: Performance Considerations
- [ ] **be-idempotency-edge-case-plan** output → fills: Edge Cases, Reliability
- [ ] **be-observability-plan** output → fills: Observability
- [ ] **be-dependency-risk-analysis** output → fills: Tradeoffs / Decisions
- [ ] **be-pattern-read** output → fills: Pattern alignment notes
- [ ] **system-flow-diagram** output (if run) → fills: High Level Diagrams

If any input is missing, run the corresponding skill first. Do not leave sections blank with "TBD".

---

## File Naming Convention

```
[feature-name]-be-design.md
```

Examples:
- `product-search-be-design.md`
- `user-onboarding-be-design.md`
- `checkout-flow-be-design.md`
- `notification-center-be-design.md`

Use kebab-case. Be specific — `feature-be-design.md` is not acceptable.

---

## The Template

Fill every section. If a section truly doesn't apply, write one sentence explaining why (e.g., "No async queue needed — this operation is synchronous and completes within the request lifecycle."). Never leave a section empty.

```markdown
# [Feature Name] — Backend Design

## User Prompt
> [Paste the exact original user request here, unchanged]

## Problem Statement
[2–4 sentences. What needs to be built, what constraints apply, what success looks like from a backend perspective.]

---

## User Goal
[1–2 sentences. What the user is actually trying to achieve — not the feature, the business intent.]

## Core Flows

### Happy Path
1. [Step 1 — e.g., Client sends POST /api/orders with payload]
2. [Step 2 — e.g., Auth middleware validates JWT, extracts userId]
3. [Step 3 — e.g., Service layer validates input, checks inventory]
4. [Step 4 — e.g., DB transaction: insert order, decrement stock]
5. [Step 5 — e.g., Enqueue confirmation email job]
6. [Step 6 — e.g., Return 201 Created with order ID]
...

### Edge Cases
- [ ] DB write fails mid-transaction → [behavior: rollback, return 500]
- [ ] Duplicate request (retry) → [behavior: idempotency key check, return cached response]
- [ ] Downstream service timeout → [behavior: circuit breaker trips, fallback or 503]
- [ ] Invalid / missing input → [behavior: 400 with structured error body]
- [ ] Unauthorized caller → [behavior: 401 / 403 with reason]
- [ ] Rate limit exceeded → [behavior: 429 with Retry-After header]
- [ ] [Feature-specific edge case] → [behavior]

---

## API Design

### Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| [METHOD] | [/path] | [Bearer / API Key / None] | [what it does] |

### Request Contract
```ts
// [METHOD] [/path]
interface [FeatureName]Request {
  [field]: [type]; // [validation rule]
}
```

### Response Contract
```ts
// Success — [HTTP status]
interface [FeatureName]Response {
  [field]: [type];
}

// Error — [HTTP status]
interface ErrorResponse {
  error: string;
  code: string;      // machine-readable error code
  details?: unknown; // optional field-level validation errors
}
```

### Status Codes
| Code | Scenario |
|------|---------|
| 200 / 201 | [success scenario] |
| 400 | [validation failure] |
| 401 | [missing / invalid auth] |
| 403 | [insufficient permissions] |
| 404 | [resource not found] |
| 409 | [conflict, e.g., duplicate] |
| 429 | [rate limited] |
| 500 | [unexpected server error] |
| 503 | [downstream dependency unavailable] |

### Versioning Strategy
- **Version**: [e.g., v1 via URL prefix /api/v1/...]
- **Breaking change policy**: [e.g., deprecation notice 30 days before removal]

---

## Data & Storage

### Schema Design
```sql
-- [table_name]
CREATE TABLE [table_name] (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  [field]     [type] NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Indexes
```sql
-- Reason: [why this index is needed]
CREATE INDEX idx_[table]_[column] ON [table]([column]);
```

### Data Access Patterns
| Query | Frequency | Strategy |
|-------|-----------|----------|
| [what is queried] | [high/med/low] | [index / cache / pagination] |

### Migration Plan
- [ ] [Migration step 1 — e.g., add column with default, backfill, then add NOT NULL]
- [ ] [Migration step 2]

### Cache Strategy
- **Cache layer**: [e.g., Redis, in-memory, CDN]
- **Cache keys**: [pattern, e.g., `user:{userId}:orders`]
- **TTL**: [value and reasoning]
- **Invalidation triggers**: [list of events that bust the cache]
- **Consistency model**: [eventual / strong]

---

## Security

### Authentication
- **Mechanism**: [e.g., JWT Bearer token via Authorization header]
- **Token validation**: [e.g., verify signature, expiry, issuer]
- **Token refresh**: [e.g., sliding window, refresh token rotation]

### Authorization
| Role / Permission | Allowed Actions | Denied Actions |
|-------------------|----------------|----------------|
| [role] | [list] | [list] |

### Input Validation
| Field | Rule | Error |
|-------|------|-------|
| [field] | [e.g., required, max 255 chars, UUID format] | [400 with code] |

### Threat Model
- **Injection**: [mitigation, e.g., parameterized queries via ORM]
- **Broken auth**: [mitigation]
- **Rate limiting**: [threshold + strategy, e.g., 100 req/min per IP via sliding window]
- **Sensitive data**: [e.g., passwords hashed with bcrypt cost 12, PII masked in logs]
- **SSRF / path traversal**: [if applicable]

---

## Async / Queue Design

> If no async processing is needed, state why: e.g., "All operations complete synchronously within the request lifecycle — no queue required."

### Jobs / Events
| Job / Event | Trigger | Worker | Retry Policy | Idempotent? |
|-------------|---------|--------|-------------|-------------|
| [name] | [trigger] | [worker] | [e.g., 3x exp backoff] | [yes/no] |

### Queue Configuration
- **Queue**: [e.g., BullMQ, SQS, Kafka topic]
- **Concurrency**: [workers per instance]
- **Dead-letter queue**: [yes/no + retention]

### Failure Handling
- **Max retries**: [n]
- **Backoff strategy**: [e.g., exponential with jitter]
- **On final failure**: [e.g., move to DLQ, alert on-call]

---

## Performance Considerations

### Query Optimization
| Query | Risk | Mitigation |
|-------|------|------------|
| [description] | [e.g., full table scan] | [e.g., add composite index] |

### Throughput & Latency Targets
| Operation | P50 Target | P99 Target | Throughput |
|-----------|-----------|-----------|------------|
| [op] | [ms] | [ms] | [req/s] |

### Scalability
- **Horizontal scaling**: [e.g., stateless service, scales via replica count]
- **Vertical bottlenecks**: [e.g., DB write throughput limited by single primary]
- **Connection pooling**: [e.g., PgBouncer, pool size = 20 per instance]

### Optimization Checklist
- [ ] [specific optimization — e.g., paginate with cursor, not OFFSET]
- [ ] [specific optimization — e.g., bulk-insert instead of N individual inserts]
- [ ] [specific optimization — e.g., defer non-critical work to background job]

---

## Reliability

### Failure Points
| Component | Failure Mode | Detection | Recovery |
|-----------|-------------|-----------|---------|
| [e.g., DB] | [e.g., connection timeout] | [health check] | [retry with backoff] |

### Idempotency
| Operation | Idempotency Key | Strategy |
|-----------|----------------|---------|
| [op] | [e.g., client-supplied request ID] | [e.g., dedup table, upsert] |

### Circuit Breaker
- **Applies to**: [downstream services that need protection]
- **Thresholds**: [e.g., open after 5 failures in 10s, half-open after 30s]
- **Fallback**: [e.g., return cached response / 503 with Retry-After]

### Data Consistency
- **Transaction scope**: [e.g., single DB, saga pattern across services]
- **Isolation level**: [e.g., READ COMMITTED, SERIALIZABLE for critical sections]
- **Compensating actions**: [e.g., if email job fails, order still persists — retry separately]

---

## Observability

### Logging
| Event | Level | Key Fields | Notes |
|-------|-------|-----------|-------|
| [e.g., request received] | INFO | [userId, requestId, path] | [structured JSON] |
| [e.g., DB query slow] | WARN | [query, duration, table] | [threshold: >500ms] |
| [e.g., unhandled error] | ERROR | [error, stack, requestId] | [never log PII] |

### Metrics
| Metric | Type | Labels | Threshold / Alert |
|--------|------|--------|------------------|
| [e.g., http_request_duration_ms] | Histogram | [method, path, status] | [P99 > 2s → alert] |
| [e.g., queue_job_failed_total] | Counter | [job_name] | [> 10/min → alert] |

### Tracing
- **Trace propagation**: [e.g., W3C TraceContext headers, OpenTelemetry]
- **Key spans**: [list critical spans to instrument, e.g., DB query, external HTTP call]
- **Sampling**: [e.g., 10% in prod, 100% on error]

### Alerting
| Alert | Condition | Severity | Runbook |
|-------|-----------|----------|---------|
| [name] | [condition] | [P1/P2/P3] | [link or description] |

---

## Tradeoffs / Decisions

| Decision | Chosen | Reason | Tradeoff |
|----------|--------|--------|---------|
| [topic] | [choice] | [why] | [cost accepted] |

### [Decision Title]
**Context**: [why this decision was needed]
**Chosen**: [what was decided]
**Why**: [specific reasons]
**Tradeoffs**: [what is accepted]
**Revisit when**: [conditions that would prompt re-evaluation]

---

## High Level Diagrams

### System Flow
[Mermaid diagram or ASCII showing end-to-end request lifecycle]

### Data Flow
[Mermaid diagram or ASCII showing how data moves between components]

### Async Flow (if applicable)
[Mermaid diagram or ASCII showing queue, workers, retry paths]

### State Machine (if applicable)
[Mermaid diagram or ASCII showing entity state transitions]

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
[What specifically is the problem? Why does it need to be solved on the backend?]

### Solution
[How is it solved? What does the implementation look like — service, repository, middleware, etc.?]

### Steps
- [ ] [Concrete implementation step — e.g., Create `src/modules/orders/orders.service.ts` with method `createOrder(dto: CreateOrderDto): Promise<Order>`]
- [ ] [Concrete implementation step]
- [ ] [Concrete implementation step]

### Tests
- [ ] [Test: describe the scenario and expected outcome — e.g., POST /api/orders with valid payload → 201 with order ID in body]
- [ ] [Test: e.g., POST /api/orders with duplicate idempotency key → 200 with original response, no new DB row]
- [ ] [Test: e.g., POST /api/orders when DB is down → 500 with structured error, transaction rolled back]

### Edge Cases Covered
- [ ] [Edge case and how this solution handles it]
- [ ] [Edge case and how this solution handles it]

---

## 2. [Problem Name]

[... repeat structure ...]
```

---

## Writing Quality Rules

**Problem Statement**: Must be concrete and backend-scoped. Bad: "We need to handle orders." Good: "We need a transactional order creation endpoint (POST /api/v1/orders) that atomically inserts an order record, decrements inventory, and enqueues a confirmation email — with idempotency support and rollback on partial failure."

**Solutions list**: Must be in implementation order — schema migration first, then repository, then service, then controller/route, then middleware. A mid-level backend engineer should be able to implement them one by one without asking questions.

**Steps**: Must be concrete and actionable. Bad: "Build the service." Good: "Create `src/modules/orders/orders.service.ts`. Add `createOrder(dto: CreateOrderDto, idempotencyKey: string): Promise<Order>`. Wrap DB inserts and inventory decrement in a single Prisma `$transaction`."

**Tests**: Must describe observable HTTP or system behavior. Bad: "Test the endpoint." Good: "POST /api/v1/orders with a valid body → 201, response body contains `{ id: UUID, status: 'pending' }`, and one new row exists in the `orders` table."

**Security section**: Must be specific. Bad: "Validate inputs." Good: "Reject requests where `quantity < 1` or `quantity > 1000` with 400 and `{ error: 'INVALID_QUANTITY', details: { quantity: 'Must be between 1 and 1000' } }`."

---

## File Output

Save to: `designs/[feature-name]-be-design.md`

The file should be self-contained. A backend engineer who wasn't part of the design discussion should be able to read it and understand:
- What is being built and why
- The full API contract (request, response, errors)
- The data schema and access patterns
- How to implement it end-to-end
- What can fail and how it is recovered
- Why the key architectural decisions were made