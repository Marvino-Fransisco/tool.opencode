---
name: be-dependency-risk-analysis
description: Use this skill when the user needs to identify and plan for risks from external dependencies in a backend feature. Triggers include: a feature that calls an external API, uses a third-party service, depends on another internal service, or relies on a message queue or cache. Also use when the user asks "what happens if X goes down", "how should I handle failures from Y", or "what are the risks of depending on Z".
---

This skill guides the systematic analysis of external and internal dependency risks in a backend feature, producing concrete failure modes and mitigation strategies.

The user provides a feature design or description. The goal is to identify every external dependency, enumerate its failure modes, and design appropriate guards.

## Analysis Framework

### Step 1 — Map all dependencies
For the given feature, list every external touchpoint:
- **External APIs** — third-party HTTP services (payment gateways, email providers, SMS, maps, AI APIs)
- **Internal services** — other microservices or modules called over the network
- **Databases** — primary DB, read replicas, separate DBs
- **Caches** — Redis, Memcached
- **Message queues** — SQS, RabbitMQ, Kafka, Pub/Sub
- **File storage** — S3, GCS, local disk
- **Auth providers** — OAuth servers, JWT issuers
- **Scheduled jobs** — cron dependencies, time-based triggers

### Step 2 — For each dependency, assess risk

Score each dependency on:
| Dimension | Questions to ask |
|---|---|
| **Criticality** | Does the feature completely fail if this dependency is unavailable? |
| **Latency sensitivity** | Is this in the critical path of a user-facing request? |
| **Reliability** | What is the dependency's known SLA/uptime? |
| **Controllability** | Can we cache, mock, or degrade gracefully without it? |

### Step 3 — Enumerate failure modes

For each dependency, identify:
- **Total outage** — service completely unreachable
- **Partial failure** — some requests fail, some succeed
- **Slow responses** — latency spikes causing request timeouts
- **Data errors** — unexpected response shapes, missing fields, bad data
- **Auth failures** — expired tokens, rotated credentials, rate limits on auth
- **Rate limiting** — 429s from the dependency under load
- **Data consistency** — dependency's data is stale or inconsistent with ours

### Step 4 — Design mitigations

For each failure mode, choose the right mitigation:

**Timeouts**
- Always set an explicit timeout on every external call — never rely on the default
- Recommended: connect timeout 2–5s, read timeout 5–30s depending on the operation

**Retries**
- Retry on transient failures (5xx, network errors, timeouts)
- Do NOT retry on client errors (4xx) — they won't fix themselves
- Use exponential backoff with jitter: `delay = base * 2^attempt + random(0, base)`
- Set a max retry count (3–5) and a max total retry duration

**Circuit breaker**
- Use when a dependency is consistently failing — stop sending requests to give it time to recover
- Three states: Closed (normal) → Open (failing, reject immediately) → Half-open (test with one request)
- Threshold: open after N failures in M seconds

**Fallbacks**
- Cached data — serve stale data if the live source is unavailable
- Default value — return a safe default instead of failing
- Degrade gracefully — skip the feature, not the whole request
- Queue for later — accept the request and process async when dependency recovers

**Idempotency**
- Any operation that can be retried MUST be idempotent
- Use idempotency keys for payment and write operations
- Check "has this already been processed?" before acting

**Bulkhead**
- Isolate dependency calls in separate thread pools / connection pools
- Prevent one slow dependency from exhausting all resources

## Output Format

For each dependency, produce:

### [Dependency Name]
- **Type**: External API / Internal service / DB / Cache / Queue
- **Criticality**: Critical (feature fails) / Degraded (feature partially works) / Optional (feature still works)
- **In critical path**: Yes / No

**Failure Modes**
| Mode | Probability | Impact | Mitigation |
|---|---|---|---|
| Total outage | Low/Med/High | Describe impact | Describe mitigation |
| Timeout / slow | Low/Med/High | Describe impact | Describe mitigation |
| Rate limited | Low/Med/High | Describe impact | Describe mitigation |
| Bad data | Low/Med/High | Describe impact | Describe mitigation |

**Configuration Recommendations**
- Timeout: Xms connect, Xms read
- Retry: X attempts, exponential backoff, retry on 5xx/timeout only
- Circuit breaker: open after X failures in Xs
- Fallback: [describe fallback behavior]

**Open Questions**
- What is the dependency's documented SLA?
- Is there a sandbox/mock available for testing failure scenarios?