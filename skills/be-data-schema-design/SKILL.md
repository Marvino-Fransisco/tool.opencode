---
name: be-data-schema-design
description: Use this skill when the user needs to design or review a database schema. Triggers include: modeling entities and relationships for a feature, choosing field types, planning indexes, designing a migration strategy, or deciding between normalized vs denormalized data. Also use when the user says "design the database for X", "what tables do I need", "how should I model this data", or "plan the migration".
---

This skill guides the design of clean, performant, and maintainable database schemas for backend features.

The user provides a feature or data requirement. They may include context about the database engine (PostgreSQL, MySQL, MongoDB, etc.), existing schema patterns, expected data volume, or read/write access patterns.

## Design Thinking

Before modeling tables or documents, understand the data's context:
- **Database engine**: Relational (PostgreSQL, MySQL) vs document (MongoDB) vs key-value?
- **Access patterns**: What queries will run most? Read-heavy or write-heavy?
- **Cardinality**: One-to-one, one-to-many, many-to-many relationships?
- **Mutability**: Will this data be updated in place or append-only (event log)?
- **Volume**: Expected rows/documents at launch vs 1 year vs 5 years?

Then design a schema that is:
- Normalized enough to avoid duplication, but not over-normalized to the point of expensive joins
- Indexed for the actual query patterns, not hypothetical ones
- Migration-safe — every change can be applied without downtime if possible

## Schema Design Guidelines

### Naming Conventions
- Tables: **plural snake_case** — `orders`, `order_items`, `user_profiles`
- Columns: **singular snake_case** — `created_at`, `user_id`, `is_active`
- Foreign keys: `{referenced_table_singular}_id` — `user_id`, `order_id`
- Indexes: `idx_{table}_{columns}` — `idx_orders_user_id_created_at`
- Follow the existing project's conventions above all else

### Standard Columns
Include these on every table unless there's a strong reason not to:
- `id` — primary key (UUID or auto-increment bigint — choose one and be consistent)
- `created_at` — timestamp with timezone, default now()
- `updated_at` — timestamp with timezone, updated on every write
- `deleted_at` — nullable, for soft deletes (if the project uses soft delete pattern)

### Relationships
- Define **foreign key constraints** explicitly — don't rely on application-level enforcement
- Specify **ON DELETE** behavior: `CASCADE`, `SET NULL`, or `RESTRICT` — never leave it implicit
- For many-to-many: use a **join table** with its own `id`, `created_at`, and the two FK columns

### Indexing Strategy
- Index every **foreign key column** (most ORMs don't do this automatically)
- Index columns used in **WHERE**, **ORDER BY**, and **JOIN ON** clauses
- Use **composite indexes** when queries filter by multiple columns together — column order matters (most selective first)
- Use **partial indexes** for filtered queries on a subset of rows (e.g., `WHERE deleted_at IS NULL`)
- Avoid over-indexing — each index slows down writes

### Data Types
- Use `timestamptz` (timestamp with timezone) over `timestamp` for all time columns
- Use `text` over `varchar(n)` in PostgreSQL unless there's a real length constraint to enforce
- Use `numeric`/`decimal` for money — never `float`
- Use `uuid` for IDs exposed externally (prevents enumeration attacks)
- Use `jsonb` sparingly — only for truly schemaless data; don't use it to avoid modeling

### Migrations
- Every schema change is a **migration file** — never modify the DB manually in production
- Migrations must be **reversible** (include a down migration)
- For zero-downtime: add columns as nullable first, backfill, then add constraint
- Never rename a column in one step — add the new column, copy data, drop the old one
- Document **breaking changes** that require coordinated deploys

## Output Format

For each entity, produce:
1. **Table/Collection name**
2. **Purpose** — one sentence
3. **Columns/Fields** — name, type, nullable, default, description
4. **Constraints** — primary key, foreign keys, unique constraints, check constraints
5. **Indexes** — name, columns, type (btree/gin/etc.), rationale
6. **Relationships** — FK targets and ON DELETE behavior
7. **Migration notes** — how to apply safely, any backfill needed
8. **Open questions** — ambiguities that need product/team input