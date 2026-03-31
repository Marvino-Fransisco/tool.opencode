---
name: dd-data-performance-patterns
description: >
  Reference guide for data performance optimization: indexing strategies, partitioning, query
  optimization, caching patterns, materialized views, and database scaling techniques.
  Use this skill whenever the user asks about making queries faster, improving database performance,
  choosing an indexing strategy, deciding how to partition a table, optimizing slow queries,
  designing a caching layer, creating materialized views, scaling a database, handling high
  read or write throughput, or asks questions like "why is my query slow", "should I add an index",
  "how should I partition this table", "what caching strategy should I use", "how do I scale my
  database", "how do I optimize this aggregation", or "how do I reduce query cost". Always consult
  this skill before recommending any performance optimization or scaling strategy for data systems.
---

# Data Performance Patterns

## 1. Indexing Strategy

### Index Decision Matrix

| Query Pattern | Recommended Index |
|---|---|
| Equality on single column | B-tree (default) |
| Range queries (`BETWEEN`, `>`, `<`) | B-tree |
| Full-text search | GIN / inverted index |
| JSONB key lookups | GIN on JSONB column |
| Geospatial queries | GiST / spatial index |
| Low-cardinality filter + sort | Partial index |
| Composite filter (col_a AND col_b) | Composite B-tree (most selective first) |

### Index Design Rules
1. Index **foreign keys** always (prevents full-table scan on joins)
2. Index columns used in **WHERE + ORDER BY** together
3. Prefer **partial indexes** for filtered queries (e.g., `WHERE status = 'active'`)
4. Avoid over-indexing write-heavy tables — each index slows INSERT/UPDATE
5. Use **covering indexes** (`INCLUDE`) to avoid heap fetches on hot read paths

```sql
-- Covering index: no heap fetch needed for this query
CREATE INDEX idx_orders_user_status ON orders (user_id, status) INCLUDE (created_at, amount_cents);
SELECT created_at, amount_cents FROM orders WHERE user_id = $1 AND status = 'paid';
```

### Index Maintenance
- Monitor index bloat (`pg_stat_user_indexes`)
- `REINDEX CONCURRENTLY` for bloated indexes
- Drop unused indexes (check `idx_scan = 0` after 30 days)

---

## 2. Partitioning Strategy

### When to Partition
- Table > 100M rows or > 50GB
- Queries almost always filter by a specific column (time, region, tenant)
- Need efficient bulk deletes (drop partition vs DELETE)

### Partition Key Selection

| Key Type | Use Case | Example |
|---|---|---|
| **Time (range)** | Time-series, events, logs | `created_at` monthly/daily |
| **List** | Known set of values | `region`, `status` |
| **Hash** | Even distribution, no natural key | `user_id % N` |
| **Composite** | Multi-tenant + time | `(tenant_id, created_at)` |

### Partition Granularity Guide

| Data Volume / Day | Partition By |
|---|---|
| < 1M rows | Monthly |
| 1M–10M rows | Weekly |
| 10M–100M rows | Daily |
| > 100M rows | Hourly |

### Partition Pruning — Make It Work
```sql
-- ✅ Partition pruning kicks in
SELECT * FROM events WHERE created_at >= '2024-01-01' AND created_at < '2024-02-01';

-- ❌ No pruning (function wrapping disables it)
SELECT * FROM events WHERE DATE_TRUNC('month', created_at) = '2024-01-01';
```

---

## 3. Query Optimization

### The EXPLAIN Checklist
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <your_query>;
```

Red flags to look for:
- `Seq Scan` on large tables → missing index
- `Hash Join` on huge tables → consider index nested loop or pre-filter
- `Sort` on large dataset → add ORDER BY column to index
- High `Buffers: shared hit` miss rate → increase `shared_buffers`
- `Rows Removed by Filter` >> actual rows → index predicate not selective

### N+1 Query Pattern
```python
# BAD: N+1 queries
for order in orders:
    user = db.query(User).filter_by(id=order.user_id).first()

# GOOD: single JOIN
orders_with_users = db.query(Order, User).join(User).all()
```

### Pagination
```sql
-- BAD: OFFSET gets slower at large offsets (full scan to skip)
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;

-- GOOD: Keyset / cursor pagination (O(log n))
SELECT * FROM orders WHERE id > :last_seen_id ORDER BY id LIMIT 20;
```

### Aggregation on Large Tables
- Pre-aggregate into summary tables during off-peak hours
- Use incremental aggregation (add new data to existing summary)
- Use approximate functions for analytics: `HyperLogLog` for COUNT DISTINCT, `percentile_approx` for p99

---

## 4. Caching Patterns

### Cache Hierarchy

```
Browser cache (static assets)
  ↓
CDN / Edge cache (API responses, public data)
  ↓
Application cache (Redis/Memcached — session, hot objects)
  ↓
Query result cache (materialized views, warehouse result cache)
  ↓
Database buffer cache (shared_buffers, InnoDB buffer pool)
```

### Cache-Aside Pattern (most common)
```python
def get_user(user_id):
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    user = db.query(User).get(user_id)
    redis.setex(f"user:{user_id}", ttl=300, value=json.dumps(user))
    return user
```

### Cache Invalidation Strategies

| Strategy | Mechanism | Use When |
|---|---|---|
| TTL expiry | Auto-expire after N seconds | Acceptable stale window |
| Write-through | Update cache on every write | Strong consistency needed |
| Write-invalidate | Delete cache key on write | Simple, slightly stale ok |
| Event-driven | Subscribe to change events | Real-time accuracy needed |

### Cache Key Design
```
{service}:{entity}:{id}:{version}
e.g. payments:user:uuid-123:v2
```

---

## 5. Materialization Patterns

### Materialized View
```sql
CREATE MATERIALIZED VIEW daily_revenue AS
SELECT DATE(created_at) AS day, SUM(amount_cents) AS revenue
FROM orders WHERE status = 'paid'
GROUP BY 1;

-- Refresh (no lock)
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_revenue;
```

### Incremental Materialization (dbt)
```sql
-- models/marts/fct_daily_revenue.sql
{{ config(materialized='incremental', unique_key='day') }}
SELECT DATE(created_at) AS day, SUM(amount_cents) AS revenue
FROM {{ ref('fct_orders') }}
{% if is_incremental() %}
  WHERE created_at >= (SELECT MAX(day) FROM {{ this }})
{% endif %}
GROUP BY 1
```

### Pre-aggregation Table Pattern
```sql
-- Populated by daily pipeline job
CREATE TABLE agg_user_activity_daily (
  user_id UUID,
  activity_date DATE,
  event_count INT,
  session_count INT,
  PRIMARY KEY (user_id, activity_date)
);
```

---

## 6. Scaling Patterns

### Read Replicas
- Route all SELECT queries to read replica
- Use primary only for writes
- Beware replication lag for read-your-own-writes scenarios

### Vertical vs Horizontal Scaling

| Approach | When | Limit |
|---|---|---|
| Vertical (bigger instance) | First option, fast | Hardware ceiling |
| Read replicas | Read-heavy | Write bottleneck remains |
| Sharding | Write-heavy, huge data | Operational complexity |
| CQRS + separate read store | Different read/write patterns | Eventual consistency |

### Sharding Key Selection
- Choose a key with **high cardinality** and **even distribution**
- Avoid keys that create **hot shards** (e.g., `created_at` — all writes go to latest shard)
- Prefer: `user_id`, `tenant_id`, `entity_id` (hashed)
- Co-locate related data: shard orders by `user_id` if most queries are per-user

### Connection Pooling
- Always use a connection pooler (PgBouncer, RDS Proxy) between app and DB
- Transaction pooling mode for high-concurrency APIs
- Session pooling mode for long-running jobs

### Cost-Performance Trade-offs

| Technique | Cost | Performance Gain |
|---|---|---|
| Add index | +storage, -write speed | High for targeted queries |
| Partition pruning | Minimal | High for time-range queries |
| Materialized view | +storage, +compute | High for repeated aggregations |
| Read replica | +instance cost | High for read-heavy loads |
| Cache layer | +infra | Very high for hot data |
| Warehouse migration | High migration cost | Very high for analytics |