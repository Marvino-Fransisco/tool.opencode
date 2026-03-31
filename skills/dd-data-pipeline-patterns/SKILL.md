---
name: dd-data-pipeline-patterns
description: >
  Reference guide for data pipeline design: ingestion strategies (batch, streaming, CDC), ETL/ELT
  transformation layers, orchestration patterns, idempotency, reprocessing, and dead-letter queues.
  Use this skill whenever the user asks about building or designing a data pipeline, choosing between
  batch and streaming, setting up CDC (change data capture), designing an ETL or ELT flow, using
  Medallion / Bronze-Silver-Gold architecture, orchestrating pipelines with Airflow or similar tools,
  handling late-arriving data, designing backfill strategies, or asks questions like "how do I move
  data from X to Y", "how should I structure my pipeline", "how do I handle pipeline failures",
  "how do I make my pipeline idempotent", or "what's the best ingestion pattern for this use case".
  Always consult this skill before recommending any pipeline or data movement design.
---

# Data Pipeline Patterns

## 1. Ingestion Patterns

### Batch Ingestion
- **Use when**: Data freshness of minutes-to-hours is acceptable
- **Trigger**: Schedule (cron), file arrival, API polling
- **Pattern**: Extract → Stage → Load → Validate → Promote

```
Source → Landing Zone (raw) → Staging (typed) → Core (validated) → Mart (aggregated)
```

### Micro-batch
- **Use when**: Near-real-time (seconds to minutes) without stream complexity
- **Tools**: Spark Structured Streaming (trigger interval), Flink, dbt + Airflow short intervals

### Full Load vs Incremental

| Mode | Use When | Risk |
|---|---|---|
| Full load | Small tables, schema changes | Slow, expensive at scale |
| Incremental (watermark) | `updated_at` column exists | Missed deletes |
| Incremental (CDC) | Full fidelity including deletes | More infra complexity |

**Watermark Incremental Pattern:**
```sql
SELECT * FROM source
WHERE updated_at > :last_run_timestamp
```
⚠️ Requires `updated_at` to be reliably maintained and indexed.

---

## 2. Transformation Patterns

### Layered Architecture (Medallion)

```
Bronze (Raw)     → exact copy of source, immutable
Silver (Cleaned) → typed, deduplicated, validated
Gold (Curated)   → business-level aggregates, marts
```

### dbt Layer Naming Convention
```
models/
├── staging/      -- stg_* : light cleaning, rename, cast
├── intermediate/ -- int_* : joins, pivots, business logic
└── marts/        -- fct_* (facts), dim_* (dimensions)
```

### Slowly Changing Data (during transform)
- Track `valid_from` / `valid_to` + `is_current` flag
- Use `MERGE` / `UPSERT` with surrogate key generation

### Aggregation Anti-patterns
- **Avoid**: Aggregating before joins (wrong grain)
- **Avoid**: Aggregating raw events directly in marts (no replay)
- **Prefer**: Keep raw events in silver, aggregate in gold

---

## 3. Orchestration Patterns

### DAG Design Principles
- One task = one logical operation (atomic, retryable)
- Avoid side effects in tasks (make them idempotent)
- Use sensors for external dependencies, not sleep/polling loops
- Set `max_active_runs=1` for critical pipelines to prevent overlap

### Dependency Patterns
```
ingest_raw → validate_raw → transform_silver → aggregate_gold → notify
                  ↓ (on failure)
            quarantine_bad_records
```

### Backfill Strategy
- Design every pipeline to accept a `logical_date` / `execution_date` parameter
- Partition output by `logical_date` to make backfills non-destructive
- Test backfill in staging before running in production

---

## 4. Streaming Patterns

### Event Time vs Processing Time
- **Event time**: when the event actually happened (preferred for analytics)
- **Processing time**: when the system received it (easier but skews metrics)
- Always capture both: `occurred_at` (event) + `ingested_at` (processing)

### Windowing Patterns

| Window | Use Case |
|---|---|
| Tumbling (fixed, non-overlapping) | Hourly/daily aggregates |
| Sliding (overlapping) | Moving averages |
| Session (activity-gap based) | User session analytics |

### Watermarking (Late Data Handling)
```python
# Allow up to 10 minutes of late data
.withWatermark("occurred_at", "10 minutes")
.groupBy(window("occurred_at", "1 hour"))
.count()
```

### Exactly-Once Semantics
- Use transactional sinks (Kafka transactions, idempotent producers)
- Track processed offsets in a durable store
- Use `event_id` dedup in the sink table

---

## 5. CDC (Change Data Capture)

### When to Use CDC
- Need full fidelity: inserts + updates + **deletes**
- Source system can't expose `updated_at` reliably
- Near-real-time replication required

### CDC Tools

| Tool | Source | Target |
|---|---|---|
| Debezium | Postgres, MySQL, MongoDB | Kafka |
| AWS DMS | RDS, Oracle, SQL Server | S3, Redshift |
| Airbyte | 300+ sources | Warehouses |
| Fivetran | SaaS APIs, DBs | Warehouses |

### CDC Output Schema (Debezium-style)
```json
{
  "op": "c|u|d|r",
  "before": { ... },
  "after": { ... },
  "ts_ms": 1234567890
}
```

### Handling Deletes in Target
- **Soft delete**: set `is_deleted=true`, `deleted_at=ts`
- **Hard delete**: physically remove (only if no audit requirement)
- **Tombstone**: insert a `DELETE` event record into event log

---

## 6. Idempotency & Reprocessing

### Making Pipelines Idempotent
1. **Use `INSERT OVERWRITE` or partition replacement** (not append)
2. **Use natural dedup keys** at the sink (`ON CONFLICT DO NOTHING`)
3. **Track run metadata** — store `pipeline_run_id` with each row
4. **Never mutate source data** from a pipeline

### Reprocessing Pattern
```
1. Identify affected partitions (date range, entity range)
2. Truncate/delete affected output partitions
3. Re-run pipeline with same logical_date params
4. Validate output row counts match expected
```

### Dead Letter Queue (DLQ) Pattern
```
Pipeline → Process record
              ↓ (on error)
         DLQ Table / Topic
              ↓ (after fix)
         Reprocess from DLQ
```

DLQ schema:
```sql
dlq_records(
  id SERIAL PK,
  pipeline_name VARCHAR,
  raw_payload JSONB,
  error_message TEXT,
  failed_at TIMESTAMPTZ,
  retried_at TIMESTAMPTZ,
  resolved BOOLEAN DEFAULT FALSE
)
```