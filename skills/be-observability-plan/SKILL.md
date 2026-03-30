---
name: be-observability-plan
description: Use this skill when the user needs to define logging, metrics, tracing, or alerting for a backend feature. Triggers include: deciding what to log, designing structured logs, defining metrics for a new service, planning distributed tracing spans, or setting up alerts. Also use when the user asks "what should I log for X", "how do I monitor this", "design the observability for Y", or "what alerts should I set up".
---

This skill guides the design of a complete observability plan — logs, metrics, traces, and alerts — for backend features and services.

The user provides a feature, service, or endpoint. The goal is to ensure that when something goes wrong in production, the team has everything they need to detect, diagnose, and fix it quickly.

## The Three Pillars

### 1. Logs — "What happened?"
Logs are the narrative record of system behavior. Design them for searchability and debuggability.

**Structured logging** (JSON) is mandatory for production:
```json
{
  "timestamp": "2024-01-01T00:00:00.000Z",
  "level": "info",
  "service": "order-service",
  "traceId": "abc123",
  "spanId": "def456",
  "userId": "uuid",
  "orderId": "uuid",
  "event": "order.created",
  "durationMs": 142,
  "message": "Order created successfully"
}
```

**Log levels — use them correctly:**
| Level | When to use |
|---|---|
| `ERROR` | An operation failed and requires attention (exception caught, external service unreachable) |
| `WARN` | Something unexpected happened but the operation succeeded (retry succeeded, fallback used, deprecated field used) |
| `INFO` | A significant business event occurred (order created, user registered, job completed) |
| `DEBUG` | Detailed technical information useful for debugging (DB query, cache hit/miss, function entry/exit) — disabled in production |

**Always log:**
- Request received (method, path, userId, traceId) — at INFO on success, at ERROR on failure
- External service calls (service name, duration, status code)
- Background job start and completion (jobId, type, duration, outcome)
- State transitions (order status changed from X to Y)
- Auth failures (failed login attempt, forbidden access — with userId and IP)
- Errors with full stack trace

**Never log:**
- Passwords, tokens, or secrets
- Full credit card numbers or PII beyond what's necessary
- Request bodies containing sensitive data (redact fields)
- High-frequency debug noise in production (per-row loop iterations)

### 2. Metrics — "How is the system performing?"
Metrics are numerical measurements over time. Design them for dashboards and alerting.

**The Four Golden Signals (Google SRE):**
| Signal | What to measure |
|---|---|
| **Latency** | How long requests take (p50, p95, p99) — separate success from error latency |
| **Traffic** | How much demand is on the system (requests/sec, jobs/sec) |
| **Errors** | Rate of failed requests (4xx, 5xx separately) |
| **Saturation** | How full the system is (CPU %, memory %, DB connection pool usage, queue depth) |

**Business metrics (equally important):**
- Orders created per minute
- Payment success/failure rate
- Email delivery rate
- Job processing rate vs queue depth

**Metric naming conventions:**
- Format: `{service}_{entity}_{action}_{unit}` 
- Examples: `order_service_requests_total`, `order_service_request_duration_seconds`, `order_service_jobs_queue_depth`
- Use standard suffixes: `_total` (counters), `_seconds` (latency histograms), `_bytes` (sizes)

**Metric types:**
- **Counter** — monotonically increasing (total requests, total errors)
- **Gauge** — current value that goes up and down (queue depth, active connections)
- **Histogram** — distribution of values (request duration, payload size) — use for latency

### 3. Traces — "Where did time go?"
Distributed tracing follows a request across service boundaries.

**Trace design for a feature:**
- Every incoming request starts a trace with a unique `traceId`
- Each logical operation is a **span**: DB query, external API call, cache lookup, background job
- Spans have: name, start time, duration, status (ok/error), and key attributes

**What to instrument:**
- HTTP handler (root span)
- Every DB query (child span) — include the query template (not values, to avoid PII)
- Every external HTTP call (child span) — include service name, method, status
- Cache operations (child span) — include hit/miss
- Background job processing (new root trace linked to parent)

**Key span attributes:**
```
db.query: "SELECT * FROM orders WHERE id = ?"
db.table: "orders"
http.method: "GET"
http.url: "https://payment-service/charge"
http.status_code: 200
user.id: "uuid"
order.id: "uuid"
```

## Alerting Design

### Alert Tiers
| Tier | Urgency | Response | Examples |
|---|---|---|---|
| **P1 — Critical** | Page on-call immediately | < 5 min | Error rate > 5%, service down, payment failures > 1% |
| **P2 — High** | Notify team, fix within hours | < 1 hour | Error rate > 1%, latency p99 > 2s, DLQ non-empty |
| **P3 — Medium** | Fix in next sprint | < 1 week | Elevated 4xx rate, cache hit rate dropping, disk > 80% |

### Alert Anti-Patterns to Avoid
- **Alert fatigue** — don't alert on every warning log or non-critical error
- **Flapping alerts** — use sustained thresholds (5min window) not instant spikes
- **Missing context** — every alert should link to a runbook and the relevant dashboard
- **Alerting on symptoms not causes** — alert on user impact (error rate, latency) not internal metrics that may not matter

### Standard Alert Set for a Feature
1. **Error rate spike** — `error_rate > 1% for 5 minutes`
2. **Latency spike** — `p99_latency > Xms for 5 minutes` (set based on SLA)
3. **Queue depth** — `queue_depth > N for 10 minutes` (jobs piling up)
4. **DLQ non-empty** — `dlq_message_count > 0` (any failed jobs need attention)
5. **External dependency errors** — `dependency_error_rate > 5% for 5 minutes`

## Output Format

### Logging Plan
- Log events to add (event name, level, fields to include)
- Fields to redact / never log
- Log format example (JSON snippet)

### Metrics Plan
- Metrics to add (name, type, labels/tags, what it measures)
- Dashboard panels to create (what to visualize)

### Tracing Plan
- Spans to instrument (name, parent, key attributes)
- Services to propagate trace context to

### Alerting Plan
| Alert name | Condition | Window | Tier | Runbook link |
|---|---|---|---|---|
| High error rate | error_rate > 1% | 5min | P2 | link |
| DLQ non-empty | dlq_count > 0 | instant | P2 | link |

### Runbook Template
For each P1/P2 alert, produce a minimal runbook:
1. **What is this alert?** — one sentence
2. **Likely causes** — ranked by probability
3. **Diagnostic steps** — what to check first, second, third
4. **Mitigation steps** — how to stop the bleeding fast
5. **Escalation** — who to contact if the above doesn't work