---
name: dd-markdown-format
description: Use this skill when the data designer agent needs to compile all design outputs into the final design document. Triggers include: "create the design file", "write the design doc", or after all other design skills have been run and the agent is ready to produce the final markdown output. This skill takes all upstream outputs (request-analyser, dd-data-modeling-patterns, dd-data-pipeline-patterns, dd-data-performance-patterns, dd-data-quality-governance) and assembles them into a single, clean markdown file following the exact template. Always run LAST.
---

This skill guides the agent to compile all data design thinking into a single, well-structured markdown file.

## Goal

Produce one markdown file that:
- Follows the exact template structure
- Is complete — no empty or placeholder sections
- Is readable by both engineers and non-engineers
- Serves as the single source of truth for the data feature design

---

## Pre-flight Checklist

Before writing the file, verify all inputs are available:

- [ ] **request-analyser** output → fills: User Goal, Problem Statement, Core Flows
- [ ] **dd-data-modeling-patterns** output → fills: Data Modeling
- [ ] **dd-data-pipeline-patterns** output → fills: Pipeline / Interface Design
- [ ] **dd-data-performance-patterns** output → fills: Performance Considerations
- [ ] **dd-data-quality-governance** output → fills: Data Quality & Validation, Security & Governance, Observability

If any input is missing, run the corresponding skill first. Do not leave sections blank with "TBD".

---

## File Naming Convention

```
[feature-name]-data-design.md
```

Examples:
- `user-activity-data-design.md`
- `order-analytics-data-design.md`
- `realtime-inventory-data-design.md`
- `customer-segmentation-data-design.md`

Use kebab-case. Be specific — `feature-data-design.md` is not acceptable.

---

## The Template

Fill every section. If a section truly doesn't apply, write one sentence explaining why (e.g., "No pipeline orchestration needed — data is written directly by the application service, not via a separate ingestion process."). Never leave a section empty.

```markdown
# [Feature Name] — Data Design

## User Prompt
> [Paste the exact original user request here, unchanged]

## Problem Statement
[2–4 sentences. What data problem needs to be solved, what constraints apply, what success looks like from a data perspective.]

---

## User Goal
[1–2 sentences. What the user is actually trying to achieve — not the feature, the business or analytical intent.]

## Core Flows

### Happy Path
1. [Step 1 — e.g., Source system emits an event / record]
2. [Step 2 — e.g., Ingestion layer picks up the record]
3. [Step 3 — e.g., Transformation applies business rules]
4. [Step 4 — e.g., Validated record written to sink / warehouse]
5. [Step 5 — e.g., Downstream consumer queries aggregated view]
...

### Edge Cases
- [ ] Source / DB failure → [behavior: e.g., retry with backoff, checkpoint preserved]
- [ ] Empty / null data → [behavior: e.g., reject with quarantine, default applied]
- [ ] Late arriving / out-of-order data → [behavior: e.g., watermark window, reprocessing trigger]
- [ ] Invalid / malformed records → [behavior: e.g., dead-letter queue, alert fired]
- [ ] Duplicate records → [behavior: e.g., idempotency key dedup, upsert strategy]
- [ ] [Feature-specific edge case] → [behavior]

---

## Data Modeling

### Data Source
| Source | Type | Freshness | Owner |
|--------|------|-----------|-------|
| [e.g., orders DB] | [DB / lake / stream / external API] | [real-time / hourly / daily] | [team] |

### Schema / Model
```sql
-- [table_or_dataset_name]
CREATE TABLE [table_name] (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  [field]      [type]      NOT NULL,
  [field]      [type],
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Relationships & Cardinality
| Entity A | Relationship | Entity B | Notes |
|----------|-------------|---------|-------|
| [entity] | [1:1 / 1:N / M:N] | [entity] | [e.g., enforced via FK / soft reference] |

### Normalization Strategy
- **Approach**: [e.g., 3NF for OLTP, star schema for OLAP, flat denormalized for analytics]
- **Reason**: [why this strategy fits the access pattern]

### Access Patterns
| Query / Operation | Frequency | Pattern |
|-------------------|-----------|---------|
| [e.g., fetch orders by userId] | [high/med/low] | [point lookup / range scan / aggregation] |

### Indexing Strategy
```sql
-- Reason: [why this index is needed]
CREATE INDEX idx_[table]_[column] ON [table]([column]);
```

### Partitioning & Sharding
- **Partition key**: [e.g., created_at by month, tenant_id]
- **Strategy**: [e.g., range partitioning, hash sharding]
- **Reason**: [performance / retention / multi-tenancy]

### Migration Plan
- [ ] [Step 1 — e.g., add new column with default, backfill in batches]
- [ ] [Step 2 — e.g., add NOT NULL constraint after backfill completes]
- [ ] [Step 3 — e.g., drop deprecated column in next release]

---

## Pipeline / Interface Design

### Ingestion Method
- **Type**: [Batch / Streaming / CDC / API pull]
- **Source connector**: [e.g., Kafka topic, S3 bucket, Debezium CDC, REST poll]
- **Frequency / Trigger**: [e.g., every 5 min, event-driven, daily at 02:00 UTC]

### Transformation Steps
| Step | Input | Transformation | Output |
|------|-------|---------------|--------|
| [no] | [source field / dataset] | [e.g., parse ISO date, enrich with lookup, compute derived field] | [output field / dataset] |

### Aggregation Logic
- **Grain**: [e.g., one row per user per day]
- **Aggregations**: [e.g., SUM(revenue), COUNT(orders), LAST(status)]
- **Window**: [e.g., tumbling 1-hour window, trailing 30-day window]

### Output / Sink
| Sink | Format | Partitioned By | Consumer |
|------|--------|---------------|---------|
| [e.g., BigQuery dataset] | [Parquet / JSON / rows] | [e.g., date, tenant_id] | [e.g., BI tool, API, ML model] |

### Scheduling & Orchestration
- **Orchestrator**: [e.g., Airflow, Prefect, dbt Cloud, Temporal]
- **DAG / Workflow**: [name and trigger]
- **SLA**: [e.g., data available by 06:00 UTC daily]
- **Backfill strategy**: [e.g., re-run by date range, idempotent tasks]

---

## Data Quality & Validation

### Validation Rules
| Field | Rule | Action on Failure |
|-------|------|------------------|
| [field] | [e.g., NOT NULL, range 0–100, valid UUID format] | [reject / quarantine / default] |

### Deduplication Strategy
- **Dedup key**: [e.g., event_id, composite key (user_id, timestamp)]
- **Mechanism**: [e.g., UPSERT on conflict, window-based dedup in stream processor]

### Null / Default Handling
| Field | Null Allowed | Default | Reason |
|-------|-------------|---------|--------|
| [field] | [yes/no] | [value or none] | [why] |

### Anomaly Detection
- **Volume check**: [e.g., alert if row count drops >20% vs 7-day avg]
- **Freshness check**: [e.g., alert if latest record is older than 2 hours]
- **Value distribution**: [e.g., alert if null rate for `user_id` exceeds 1%]

### Reconciliation Strategy
- **Source vs sink check**: [e.g., daily row count reconciliation between source DB and warehouse]
- **Reprocessing trigger**: [e.g., manual backfill DAG, automatic on reconciliation failure]

---

## Error Handling & Feedback

### Expected Failure Scenarios
| Scenario | Detection | Impact |
|----------|-----------|--------|
| [e.g., source DB unavailable] | [health check / timeout] | [pipeline pauses, no data loss] |
| [e.g., malformed record] | [schema validation] | [record quarantined, rest continues] |

### Retry & Reprocessing Strategy
- **Transient failures**: [e.g., 3 retries with exponential backoff, max 5 min delay]
- **Permanent failures**: [e.g., route to dead-letter topic after max retries]
- **Reprocessing**: [e.g., re-run from last checkpoint, replay from source with idempotent writes]

### Dead-Letter / Quarantine Handling
- **Storage**: [e.g., `quarantine.failed_records` table / DLQ topic]
- **Schema**: [e.g., original payload + error reason + timestamp + pipeline version]
- **Review process**: [e.g., daily alert, manual triage dashboard, auto-retry after fix]

### Alerting on Data Quality Issues
| Alert | Condition | Severity | Channel |
|-------|-----------|----------|---------|
| [name] | [condition] | [P1/P2/P3] | [Slack / PagerDuty] |

---

## Performance Considerations

### Query Optimization
| Query | Risk | Mitigation |
|-------|------|------------|
| [description] | [e.g., full table scan, N+1 joins] | [e.g., materialized view, composite index, pre-aggregation] |

### Caching Strategy
- **Cache layer**: [e.g., Redis, materialized view, query result cache]
- **Cache key pattern**: [e.g., `report:{tenantId}:{date}`]
- **TTL**: [value and reasoning]
- **Invalidation**: [event-driven / TTL-only / manual]

### Partitioning for Performance
- **Partition key**: [field + rationale]
- **Pruning benefit**: [e.g., queries on last 7 days scan only 7 partitions]
- **Estimated partition size**: [e.g., ~10M rows/month]

### Async / Queue Processing
- **Use case**: [e.g., heavy aggregation deferred to background job]
- **Queue**: [e.g., Kafka, SQS, BullMQ]
- **Expected latency**: [e.g., results available within 60s of trigger]

### Optimization Checklist
- [ ] [e.g., use LIMIT + cursor pagination instead of OFFSET for large datasets]
- [ ] [e.g., pre-aggregate daily summaries in a separate table to avoid runtime GROUP BY]
- [ ] [e.g., columnar storage format (Parquet) for analytical queries]

---

## Security & Governance

### Authentication & Authorization
| Role | Access Level | Scope |
|------|-------------|-------|
| [e.g., analyst] | [READ] | [specific dataset / masked fields] |
| [e.g., pipeline service] | [READ + WRITE] | [raw ingestion tables only] |

- **Mechanism**: [e.g., RBAC via IAM roles, row-level security in warehouse]

### Data Classification
| Field | Classification | Reason |
|-------|---------------|--------|
| [e.g., email] | PII | [directly identifies user] |
| [e.g., revenue] | Sensitive | [financial data] |
| [e.g., product_id] | Public | [no sensitivity] |

### Masking & Encryption
- **At rest**: [e.g., AES-256 encryption on storage layer]
- **In transit**: [e.g., TLS 1.2+ enforced on all connections]
- **Column masking**: [e.g., email shown as `j***@example.com` for non-admin roles]
- **Tokenization**: [e.g., PII replaced with stable token for analytics use]

### Retention & Deletion Policy
| Dataset | Retention | Deletion Mechanism | Legal Basis |
|---------|-----------|-------------------|-------------|
| [name] | [e.g., 2 years] | [e.g., partition drop, TTL] | [e.g., GDPR, internal policy] |

### Audit Trail
- **What is logged**: [e.g., all read/write access to PII tables]
- **Storage**: [e.g., `audit.access_log` table, immutable append-only]
- **Retention**: [e.g., 7 years per compliance requirement]

---

## Observability

### Logging
| Event | Level | Key Fields | Notes |
|-------|-------|-----------|-------|
| [e.g., record ingested] | INFO | [source, record_id, pipeline_run_id] | [structured JSON, no PII] |
| [e.g., validation failed] | WARN | [record_id, field, rule, value] | [route to quarantine] |
| [e.g., pipeline failed] | ERROR | [pipeline, run_id, error, stage] | [trigger alert] |

### Metrics
| Metric | Type | Labels | Threshold / Alert |
|--------|------|--------|------------------|
| [e.g., records_ingested_total] | Counter | [source, pipeline] | [drop >20% vs baseline → alert] |
| [e.g., pipeline_run_duration_seconds] | Histogram | [pipeline, dag] | [P99 > SLA → alert] |
| [e.g., data_freshness_lag_seconds] | Gauge | [dataset] | [> 2h → P2 alert] |

### Lineage Tracking
- **Tool**: [e.g., OpenLineage, dbt lineage graph, DataHub, manual docs]
- **Tracked**: [source tables → transformations → output datasets]
- **Access**: [e.g., DataHub UI, dbt docs site]

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

### Data Flow
[Mermaid diagram or ASCII showing source → ingestion → transformation → sink]

### Schema / Entity Relationship
[Mermaid diagram or ASCII showing tables and relationships]

### Pipeline / DAG
[Mermaid diagram or ASCII showing orchestration steps and dependencies]

### Lineage (if applicable)
[Mermaid diagram or ASCII showing upstream → dataset → downstream consumers]

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
[What specifically is the data problem? Why does it need to be solved?]

### Solution
[How is it solved? What schema change, pipeline step, or governance rule resolves it?]

### Steps
- [ ] [Concrete step — e.g., Create migration `V003__add_orders_partitioning.sql` partitioning `orders` by `created_at` monthly]
- [ ] [Concrete step — e.g., Add `dedup_key` column with UNIQUE constraint on `(user_id, event_type, event_timestamp)`]
- [ ] [Concrete step — e.g., Update dbt model `stg_orders.sql` to apply validation rule: filter rows where `amount < 0`]

### Tests
- [ ] [Test: describe the scenario and expected outcome — e.g., Insert duplicate event with same dedup_key → second insert ignored, row count unchanged]
- [ ] [Test: e.g., Ingest record with null `user_id` → record routed to `quarantine.failed_records`, pipeline continues]
- [ ] [Test: e.g., Query `orders` for last 7 days → query plan shows partition pruning, scans ≤ 7 partitions]

### Edge Cases Covered
- [ ] [Edge case and how this solution handles it]
- [ ] [Edge case and how this solution handles it]

---

## 2. [Problem Name]

[... repeat structure ...]
```

---

## Writing Quality Rules

**Problem Statement**: Must be concrete and data-scoped. Bad: "We need to store orders." Good: "We need a partitioned `orders` table supporting 10M rows/month with sub-100ms point lookups by `user_id`, plus a daily aggregation pipeline that materializes revenue summaries into the analytics warehouse by 06:00 UTC."

**Solutions list**: Must be in implementation order — schema / migration first, then ingestion, then transformation, then aggregation, then quality checks, then observability. A mid-level data engineer should be able to implement them one by one without asking questions.

**Steps**: Must be concrete and actionable. Bad: "Set up the pipeline." Good: "Create dbt model `int_orders_daily.sql` that aggregates `stg_orders` by `(user_id, date)`, computing `SUM(amount) AS daily_revenue` and `COUNT(*) AS order_count`. Add `unique` and `not_null` tests on `(user_id, date)` in `schema.yml`."

**Tests**: Must describe observable data behavior. Bad: "Test the pipeline." Good: "Run pipeline with a batch containing 2 records sharing the same `event_id` → output table contains exactly 1 row for that `event_id`, quarantine table contains 0 rows."

**Security section**: Must be specific. Bad: "Mask PII." Good: "Apply BigQuery column-level security policy on `users.email` — analysts with role `analyst` see `j***@example.com`, only `data-eng` service account sees the raw value."

---

## File Output

Save to: `designs/[feature-name]-data-design.md`

The file should be self-contained. A data engineer or analyst who wasn't part of the design discussion should be able to read it and understand:
- What data problem is being solved and why
- The full schema, relationships, and access patterns
- How data flows from source to sink
- What quality checks and governance rules apply
- What can fail and how it recovers
- Why the key modeling and pipeline decisions were made