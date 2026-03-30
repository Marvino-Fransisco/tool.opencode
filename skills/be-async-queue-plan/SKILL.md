---
name: be-async-queue-plan
description: Use this skill when the user needs to decide whether to process something asynchronously and how to design the async flow. Triggers include: a feature that sends emails, processes files, calls slow external APIs, does heavy computation, or needs to decouple producers from consumers. Also use when the user asks "should this be async", "how should I use a queue for X", "design the worker for Y", or "handle this in the background".
---

This skill guides the decision of when to use asynchronous processing and how to design the queue, job, and worker architecture for backend features.

The user provides a feature or operation. The goal is to decide whether async is appropriate and, if so, design the full flow: job publishing, queue configuration, worker logic, and failure handling.

## Decision Framework: Sync vs Async

Use async processing when ANY of these are true:
- The operation takes > 500ms and the user doesn't need the result immediately
- The operation calls an external service that could be slow or unavailable
- The operation is not critical to the immediate user response (sending a welcome email)
- The operation needs to be retried on failure without blocking the user
- The operation should be rate-limited or throttled (e.g., don't spam an external API)
- The operation processes a large batch that doesn't fit in a single request timeout

Keep it synchronous when:
- The user needs the result to continue (payment authorization, inventory check)
- The operation is fast and reliable (< 100ms, no external dependencies)
- Eventual consistency is not acceptable for this operation

## Async Architecture Patterns

### Pattern 1 — Fire and Forget
Best for: sending notifications, logging, analytics events, webhooks.
```
Request → API (validates, publishes job) → 200 OK
                                        ↓
                              Queue → Worker → Done
```
API returns immediately. User never sees the result of the job.

### Pattern 2 — Async with Status Polling
Best for: file processing, report generation, long-running exports.
```
Request → API (creates job record, publishes job) → 202 Accepted {jobId}
                                                  ↓
                                        Queue → Worker → updates job record
Client → GET /jobs/:id → {status: "processing" | "done" | "failed", result}
```
Client polls for status. API returns a job ID immediately.

### Pattern 3 — Async with Webhook Callback
Best for: third-party integrations, partner APIs, long operations where polling is impractical.
```
Request → API (creates job, publishes, registers callback URL) → 202 Accepted
                                                               ↓
                                                   Queue → Worker → POST callback_url {result}
```

### Pattern 4 — Event-driven (Pub/Sub)
Best for: decoupled services, fan-out (one event triggers multiple consumers), audit trails.
```
Service A → publishes event (e.g., "order.placed")
                ↓
         Topic / Exchange
        /        |        \
  Email       Inventory   Analytics
  Service     Service     Service
```

## Job Design

### Job Payload
Design the job payload to be:
- **Self-contained** — include all data needed to process the job, or just the IDs needed to fetch it
- **Immutable** — don't rely on mutable state that might change between publish and process
- **Versioned** — include a `version` field so workers can handle schema changes gracefully

```json
{
  "version": 1,
  "type": "send_welcome_email",
  "userId": "uuid",
  "email": "user@example.com",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

### Idempotency in Workers
Workers MUST be idempotent — the same job may be delivered more than once:
1. Check if the job has already been processed (using a deduplication key)
2. Process the job
3. Mark the job as processed

### Retry Strategy
Configure per job type:
- **Max attempts**: 3–5 for transient failures, 1 for non-retriable errors
- **Backoff**: exponential with jitter (prevents retry storms)
- **Retry on**: network errors, 5xx from external services, timeout
- **Do NOT retry on**: validation errors, 4xx from external services, business logic errors

### Dead Letter Queue (DLQ)
All queues must have a DLQ:
- Jobs that exhaust all retries go to the DLQ
- DLQ jobs trigger an alert
- Ops team can inspect, fix, and re-queue DLQ jobs manually

## Queue Configuration

| Configuration | Recommendation |
|---|---|
| **Visibility timeout** | 2–3x the expected max processing time |
| **Message retention** | 7–14 days (DLQ: 14 days) |
| **Max receive count** | 3–5 (before moving to DLQ) |
| **Batch size** | 1 for critical jobs; 10–100 for bulk/batch jobs |
| **Concurrency** | Start low (2–5 workers), scale based on queue depth |

## Worker Design

### Worker Structure
```
1. Receive job from queue
2. Parse and validate job payload
3. Check idempotency (has this been processed?)
4. Acquire any needed locks (if concurrent processing is risky)
5. Process the job
6. Mark as complete / update status
7. Acknowledge message (remove from queue)
   OR on failure: let visibility timeout expire for retry
```

### Error Classification
- **Retriable error**: network issue, external service 5xx, timeout → do NOT acknowledge, let it retry
- **Non-retriable error**: invalid payload, business rule violation → acknowledge (remove from queue) and log to error tracker
- **Poison message**: a job that always fails regardless of retries → move to DLQ after max attempts

## Output Format

### Decision
- Sync or Async? Rationale.
- Which pattern? (Fire and forget / Status polling / Webhook / Pub-Sub)

### Job Design
- Job type name
- Payload schema
- Idempotency key strategy

### Queue Configuration
- Queue name(s)
- Visibility timeout, retention, max receive count
- DLQ configuration

### Worker Design
- Processing steps (numbered)
- Retry strategy (attempts, backoff, what to retry)
- Error classification (retriable vs non-retriable)
- Idempotency check implementation

### Flow Diagram
Mermaid sequence diagram showing the full async flow including success and failure paths.

### Monitoring
- Metrics to track: queue depth, processing time, failure rate, DLQ count
- Alerts: DLQ non-empty, queue depth > threshold, worker error rate > X%