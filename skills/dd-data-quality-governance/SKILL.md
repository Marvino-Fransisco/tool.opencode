---
name: dd-data-quality-governance
description: >
  Reference guide for data quality frameworks and data governance: quality dimensions, validation
  patterns, PII classification and masking, GDPR/right-to-erasure, retention policies, RBAC access
  control, audit trails, and data contracts.
  Use this skill whenever the user asks about data quality, data validation rules, handling PII or
  sensitive data, data governance policies, GDPR compliance, data retention, access control for
  data, audit logging for data changes, data contracts between teams, or asks questions like
  "how do I validate my data", "how should I handle PII", "how do I implement GDPR erasure",
  "how do I control who can access what data", "how do I set up an audit trail for data changes",
  "what retention policy should I use", or "how do I define a data contract". Always consult this
  skill before designing any system that handles sensitive data or requires data quality enforcement.
---

# Data Quality & Governance

## 1. Data Quality Dimensions

| Dimension | Definition | How to Measure |
|---|---|---|
| **Completeness** | No missing required fields | % of non-null values per column |
| **Accuracy** | Values reflect reality | Cross-validate with source system |
| **Consistency** | Same value across systems | Hash comparison, row count diffs |
| **Timeliness** | Data freshness meets SLA | `MAX(updated_at)` vs current time |
| **Uniqueness** | No duplicate records | COUNT vs COUNT DISTINCT on PK |
| **Validity** | Values conform to domain rules | Regex, range, enum checks |
| **Integrity** | FK relationships hold | Orphan record counts |

---

## 2. Validation Patterns

### Schema Validation (at ingestion)
```python
SCHEMA = {
  "user_id": {"type": "uuid", "nullable": False},
  "email": {"type": "email", "nullable": False},
  "plan": {"type": "enum", "values": ["free", "pro", "enterprise"]},
  "created_at": {"type": "timestamp", "nullable": False},
}
```

### Row-level Validation (in pipeline)
```sql
-- Completeness check
SELECT COUNT(*) FILTER (WHERE email IS NULL) AS null_emails FROM staging_users;

-- Uniqueness check
SELECT user_id, COUNT(*) FROM staging_users GROUP BY user_id HAVING COUNT(*) > 1;

-- Referential integrity
SELECT s.order_id FROM staging_orders s
LEFT JOIN dim_users u ON s.user_id = u.user_id
WHERE u.user_id IS NULL;
```

### Statistical / Anomaly Checks
- Row count delta > ±20% vs previous run → alert
- Column null rate change > 5pp → alert
- Aggregate value (sum/avg) change > ±30% → alert

### dbt Test Patterns
```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: user_id
        tests: [not_null, relationships: {to: ref('dim_users'), field: user_id}]
      - name: status
        tests: [accepted_values: {values: [pending, paid, cancelled]}]
```

---

## 3. PII & Sensitive Data Handling

### PII Classification Tiers

| Tier | Examples | Handling |
|---|---|---|
| **High** | SSN, passport, financial account | Encrypt at rest + in transit, mask in logs, restrict access |
| **Medium** | Email, phone, IP address, name | Pseudonymize, restrict to need-to-know |
| **Low** | Country, timezone, age bracket | Standard access controls |

### Pseudonymization vs Anonymization
- **Pseudonymization**: Replace PII with a reversible token (can re-identify with key) — use for operational data
- **Anonymization**: Irreversible removal of PII — use for analytics/reporting exports

### Masking Strategies
```sql
-- Static masking (for non-prod environments)
UPDATE users SET email = CONCAT('user_', id, '@example.com');

-- Dynamic masking (column-level security in warehouse)
CREATE MASKING POLICY mask_email AS (val STRING) RETURNS STRING →
  CASE WHEN CURRENT_ROLE() IN ('ANALYST') THEN '***@***.***'
       ELSE val END;
```

### Encryption
- Always encrypt at-rest: use storage-level encryption (AES-256)
- Field-level encryption for highest sensitivity (SSN, payment data)
- Never store plaintext secrets or tokens in data tables

---

## 4. Retention & Deletion Policies

### Retention Schedule Template

| Data Type | Retention | Reason |
|---|---|---|
| Raw event logs | 90 days hot, 1 year cold | Debugging, reprocessing |
| Aggregated metrics | 2 years hot | Business reporting |
| User PII | Duration of account + 30 days | GDPR/legal |
| Audit logs | 7 years | Compliance |
| Backups | 30 days | Recovery |

### GDPR / Right to Erasure Pattern
```sql
-- Soft delete user data
UPDATE users SET
  email = NULL,
  phone = NULL,
  name = 'DELETED',
  deleted_at = NOW(),
  gdpr_erased_at = NOW()
WHERE user_id = :user_id;

-- Mark related records
UPDATE orders SET user_id = NULL WHERE user_id = :user_id;
```

For analytics tables: replace user identifiers with a tombstone hash.

### Archival Strategy
```
Hot storage (0–90 days)   → Primary DB / Data Warehouse
Warm storage (90d–1yr)    → Compressed parquet on object storage
Cold storage (1yr+)       → Glacier / Archive tier
Deleted (per policy)      → Purge with audit record of deletion
```

---

## 5. Access Control Patterns

### RBAC Data Warehouse Pattern

```sql
-- Roles
CREATE ROLE analyst;       -- Read-only, masked PII
CREATE ROLE engineer;      -- Read/write, unmasked non-PII
CREATE ROLE data_admin;    -- Full access

-- Grant patterns
GRANT SELECT ON ALL TABLES IN SCHEMA gold TO analyst;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA silver TO engineer;
REVOKE SELECT ON TABLE users FROM analyst;       -- PII table
GRANT SELECT ON VIEW users_masked TO analyst;    -- Masked view
```

### Row-Level Security (RLS)
```sql
-- Users only see their own org's data
CREATE POLICY org_isolation ON orders
  USING (org_id = current_setting('app.current_org_id')::UUID);
```

### Column-Level Security
- Use views or dynamic masking policies to hide sensitive columns per role
- Document which roles can access which columns in a data catalog

---

## 6. Audit Trail Design

### System Audit Columns (add to every table)
```sql
created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
created_by    UUID REFERENCES users(id),
updated_by    UUID REFERENCES users(id)
```

### Change Log Table Pattern
```sql
CREATE TABLE audit_log (
  id            BIGSERIAL PRIMARY KEY,
  table_name    VARCHAR NOT NULL,
  record_id     UUID NOT NULL,
  operation     VARCHAR NOT NULL CHECK (operation IN ('INSERT','UPDATE','DELETE')),
  old_values    JSONB,
  new_values    JSONB,
  changed_by    UUID,
  changed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Populate via database triggers or application-level interceptors.

---

## 7. Data Contracts

A data contract is a formal agreement between a data producer and consumer about schema, SLAs, and quality.

### Contract Schema (YAML)
```yaml
contract:
  name: orders_v2
  owner: payments-team
  version: 2.1.0
  sla:
    freshness: 15 minutes
    availability: 99.9%
  schema:
    - name: order_id
      type: uuid
      nullable: false
      unique: true
    - name: amount_cents
      type: integer
      nullable: false
      description: Order total in cents
  quality:
    - rule: no_nulls
      column: order_id
    - rule: row_count_delta_pct < 20
  breaking_changes:
    policy: notify_consumers_7_days
```

### Contract Versioning
- **Patch** (1.0.0 → 1.0.1): adding nullable column, adding index
- **Minor** (1.0.0 → 1.1.0): adding non-null column with default
- **Major** (1.0.0 → 2.0.0): renaming column, changing type, dropping column