---
name: dd-data-modeling-patterns
description: >
  Reference guide for data modeling decisions: schema design, normalization strategies, ERD patterns,
  star/snowflake schemas, SCD Type 2, event models, and common anti-patterns.
  Use this skill whenever the user asks about how to model data, design a schema, choose between
  normalization strategies, design a data warehouse schema, model entities and relationships, handle
  slowly changing dimensions, design an event log, or asks questions like "how should I structure
  this table", "should I normalize or denormalize", "how do I model this relationship", "what's the
  best schema for analytics", or "how do I track historical changes in data". Always consult this
  skill before recommending any schema or data model design.
---

# Data Modeling Patterns

## 1. Normalization Strategies

| Strategy | Use When | Trade-off |
|----------|----------|-----------|
| **3NF** | OLTP, high write throughput, strong consistency | More joins at read time |
| **Denormalized / Flat** | OLAP, analytics, read-heavy | Redundancy, update anomalies |
| **Hybrid** | Mixed workloads (HTAP) | Complexity in sync |

**Decision rule:**
- Write-heavy + transactional → normalize (3NF)
- Read-heavy + analytics → denormalize or materialize
- Mixed → separate OLTP + OLAP layers with a sync pipeline

---

## 2. Analytical Schema Patterns

### Star Schema
- **Fact table**: measurable events (orders, clicks, payments)
- **Dimension tables**: descriptive context (users, products, dates)
- Best for: BI tools, aggregations, slice-and-dice queries
- Constraint: denormalized dimensions increase storage

```
fact_orders
  ├── dim_users (user_id FK)
  ├── dim_products (product_id FK)
  └── dim_dates (date_id FK)
```

### Snowflake Schema
- Normalized dimensions (sub-dimensions)
- Best for: large dimension tables with hierarchies
- Trade-off: more joins, harder to query

### One Big Table (OBT)
- All dimensions pre-joined into a single wide table
- Best for: ad-hoc analytics, data marts
- Trade-off: massive storage, hard to update

---

## 3. Entity Relationship Design

### Cardinality Rules
| Relationship | Implementation |
|---|---|
| One-to-One | FK on either table or merge into one |
| One-to-Many | FK on the "many" side |
| Many-to-Many | Junction / bridge table with composite PK |

### Surrogate vs Natural Keys
- **Surrogate** (UUID, auto-increment): preferred for PKs — stable, no business logic leakage
- **Natural** (email, SSN): use only as unique constraints, not PKs

### Soft Deletes
```sql
is_deleted BOOLEAN DEFAULT FALSE
deleted_at TIMESTAMP NULL
```
Use when: audit requirements, recovery needed, referential integrity must hold.
Avoid when: data volume is huge and ghost rows degrade query performance — use archive tables instead.

---

## 4. Document & Semi-structured Models

### When to use JSONB / document columns
- Attributes are sparse and user-defined
- Schema evolves frequently
- Not queried in WHERE or JOIN conditions

### Anti-pattern to avoid
```sql
-- BAD: querying inside JSON in hot paths
SELECT * FROM users WHERE metadata->>'plan' = 'pro';

-- BETTER: promote frequently-queried keys to columns
ALTER TABLE users ADD COLUMN plan VARCHAR GENERATED ALWAYS AS (metadata->>'plan') STORED;
```

---

## 5. Event & Time-Series Models

### Immutable Event Log
```sql
events(id, entity_id, event_type, payload JSONB, occurred_at TIMESTAMPTZ)
```
- Never update or delete rows
- Partition by `occurred_at` (monthly or daily)
- Use for audit logs, activity feeds, analytics

### Snapshot + Delta Pattern
- Store full snapshots at intervals
- Store deltas between snapshots
- Reconstruct state by replaying deltas from last snapshot

### SCD Type 2 (Slowly Changing Dimensions)
```sql
dim_users(
  surrogate_key SERIAL PK,
  user_id UUID,
  email VARCHAR,
  plan VARCHAR,
  valid_from TIMESTAMPTZ,
  valid_to TIMESTAMPTZ,   -- NULL = current record
  is_current BOOLEAN
)
```

---

## 6. Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| EAV (Entity-Attribute-Value) | Impossible to query efficiently | Use JSONB or separate tables |
| God table | Single table with 100+ columns | Normalize into related tables |
| Storing aggregates only | Can't recompute if logic changes | Store raw events + materialize aggregates |
| Using VARCHAR for all types | No type safety, slow comparisons | Use proper types (INT, BOOL, TIMESTAMP) |
| No created_at/updated_at | Can't do incremental syncs | Always add audit timestamps |
| Nullable FKs everywhere | Unclear relationships | Make FKs NOT NULL where relationship is mandatory |