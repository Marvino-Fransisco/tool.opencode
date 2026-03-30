---
name: be-query-optimization
description: Use this skill when the user needs to optimize database queries or data access patterns. Triggers include: a query is slow, N+1 query problem, missing indexes, designing a caching layer, reviewing ORM-generated queries, or planning how data will be fetched for a new feature. Also use when the user says "this query is slow", "how should I index this", "should I cache this", "avoid N+1", or "optimize the data layer for X".
---

This skill guides the diagnosis and optimization of database query performance and data access patterns in backend systems.

The user provides a query, ORM code, or feature description. The goal is to identify performance problems before they reach production and design efficient data access patterns.

## Diagnosis Framework

### Step 1 — Understand the access pattern
Before optimizing, know:
- **Read vs write ratio** — is this read-heavy (optimize for reads) or write-heavy (be careful with indexes)?
- **Query frequency** — called once per page load or once per item in a list?
- **Data volume** — 1,000 rows or 100,000,000 rows?
- **Latency requirement** — background job (seconds ok) or user-facing request (< 100ms)?

### Step 2 — Identify the problem type

| Symptom | Likely problem |
|---|---|
| Query slow on large tables | Missing index |
| Query slow despite index | Wrong index, index not being used, too many rows returned |
| Many small queries in a loop | N+1 query problem |
| Repeated identical queries | Missing cache |
| Joins across multiple large tables | Need denormalization or materialized view |
| Aggregations on large datasets | Need pre-aggregation or analytics DB |
| Write contention / deadlocks | Over-locking, poor transaction design |

### Step 3 — Read the query plan
For PostgreSQL, always check:
```sql
EXPLAIN ANALYZE SELECT ...
```
Look for:
- `Seq Scan` on large tables — needs an index
- `Index Scan` — good, but check the rows estimate vs actual
- `Hash Join` vs `Nested Loop` — nested loop is expensive when the outer set is large
- High `actual rows` vs low `estimated rows` — stale statistics, run `ANALYZE`
- `Sort` on unindexed columns — add index or avoid the sort

## Optimization Strategies

### Indexing
- **Single-column index**: for filters on one column (`WHERE user_id = ?`)
- **Composite index**: for queries filtering on multiple columns — order matters: put the most selective column first, then columns used in ORDER BY
- **Partial index**: for queries that always filter by a condition (`WHERE deleted_at IS NULL`)
- **Covering index**: include all columns the query needs so it never hits the table (`INCLUDE (col1, col2)` in PostgreSQL)
- **GIN index**: for full-text search, array contains, JSONB queries

**Index anti-patterns to avoid:**
- Indexing low-cardinality columns (boolean, status with 2-3 values) — rarely helps
- Too many indexes on write-heavy tables — each index slows inserts/updates
- Unused indexes — check `pg_stat_user_indexes` for zero-scans

### N+1 Query Elimination
N+1 occurs when fetching a list then querying for each item:
```js
// BAD — N+1
const orders = await Order.findAll();
for (const order of orders) {
  order.user = await User.findById(order.userId); // N queries
}

// GOOD — eager load
const orders = await Order.findAll({ include: [User] }); // 1 JOIN query

// OR — batch load
const userIds = orders.map(o => o.userId);
const users = await User.findAll({ where: { id: userIds } }); // 1 IN query
```

Always prefer:
1. SQL JOINs for related data needed in the same query
2. Batched `WHERE id IN (...)` for separate lookups
3. Dataloader pattern for GraphQL resolvers

### Caching Strategy

| Data type | Cache strategy | TTL |
|---|---|---|
| User session / token | Redis string | Token expiry |
| Frequently read, rarely changed (config, catalog) | Redis + cache-aside | Minutes to hours |
| Computed aggregates (counts, totals) | Redis + write-through or scheduled refresh | Seconds to minutes |
| User-specific data | Redis with user-scoped key | Short (30s–5min) |
| Search results | Redis + cache-aside | Short (10s–60s) |

**Cache invalidation rules:**
- Always invalidate on write to the source of truth
- Never cache mutable user-generated content with long TTLs
- Use versioned cache keys when the data shape changes: `user:v2:{id}`

**Cache-aside pattern:**
```
1. Check cache for key
2. If hit: return cached value
3. If miss: query DB, store in cache, return value
```

### Pagination
Never use `OFFSET` on large datasets — it gets slower as the page number increases:
```sql
-- BAD for large tables
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 10000;

-- GOOD — cursor-based pagination
SELECT * FROM orders
WHERE created_at < :cursor
ORDER BY created_at DESC
LIMIT 20;
```

Use cursor-based (keyset) pagination for any table that will grow large.

### Query Reduction
- **Select only needed columns** — avoid `SELECT *` in production queries
- **Count approximations** — use `reltuples` from `pg_class` for approximate counts instead of `COUNT(*)`
- **Batch writes** — bulk insert/update instead of row-by-row
- **Defer non-critical work** — move slow writes to background jobs if they don't need to be synchronous

## Output Format

### Performance Assessment
- Identified query problems (with code snippets if provided)
- Estimated severity (low / medium / high)
- Root cause analysis

### Index Recommendations
For each recommended index:
- Table and column(s)
- Index type and rationale
- DDL statement: `CREATE INDEX CONCURRENTLY idx_... ON ... (...)`
- Expected impact

### Query Rewrites
Before/after for each problematic query with explanation.

### Caching Plan
- What to cache
- Cache key pattern
- TTL recommendation
- Invalidation trigger

### Monitoring
- Queries to watch (flag if > Xms)
- Metrics to track (cache hit rate, query count per request, p99 latency)