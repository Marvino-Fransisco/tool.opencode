---
name: be-api-contract-design
description: Use this skill when the user needs to design or review API endpoints. Triggers include: designing a new REST or GraphQL API, defining request/response schemas, planning versioning strategy, choosing HTTP status codes, or documenting an API contract for a feature. Also use when the user says "design an endpoint", "what should the API look like", or "define the contract for X".
---

This skill guides the design of clear, consistent, and production-grade API contracts for backend features.

The user provides a feature or capability to expose via API. They may include context about the consumers (frontend, mobile, third-party), existing API patterns, or constraints (REST vs GraphQL, auth model, etc.).

## Design Thinking

Before defining endpoints, understand the API's context:
- **Consumer**: Who calls this API? Frontend, mobile, service-to-service, third-party?
- **Action type**: Is this a CRUD operation, a command, a query, or an event trigger?
- **Idempotency requirement**: Can this be safely retried?
- **Auth scope**: What level of access is required to call this?

Then commit to a contract that is:
- Consistent with existing project conventions (naming, casing, envelope structure)
- Explicit about every possible response (success, validation error, auth error, not found, server error)
- Versioned with a clear strategy (URI versioning `/v1/`, header versioning, etc.)

## Contract Design Guidelines

### Endpoint Design
- Use **resource-oriented** naming for REST: `POST /orders`, `GET /orders/:id`, `PATCH /orders/:id/status`
- Avoid verbs in REST URLs (use HTTP method as the verb)
- For actions that don't map to CRUD, use sub-resources or command endpoints: `POST /orders/:id/cancel`
- For GraphQL, define Query vs Mutation clearly; mutations must be idempotent where possible

### Request Schema
Define every field with:
- **Name** and **type**
- **Required vs optional**
- **Validation rules** (min/max, format, enum values)
- **Default value** if applicable

### Response Schema
Always define:
- **Success response** (200/201) with full payload shape
- **Validation error** (400) with field-level error structure
- **Auth errors** (401 unauthorized, 403 forbidden)
- **Not found** (404) with consistent error envelope
- **Server error** (500) with safe, non-leaking message

### Status Code Conventions
| Scenario | Code |
|---|---|
| Resource created | 201 |
| Async job accepted | 202 |
| No content (DELETE) | 204 |
| Validation failed | 400 |
| Not authenticated | 401 |
| Authenticated but forbidden | 403 |
| Resource not found | 404 |
| Conflict (duplicate) | 409 |
| Rate limited | 429 |
| Server error | 500 |

### Versioning
- Choose one strategy and apply it project-wide
- URI versioning (`/v1/`) is simplest and most explicit
- Header versioning (`API-Version: 2024-01`) is cleaner for clients
- Never break existing contracts — add fields, don't remove them

### Error Envelope
Standardize error responses across the entire API:
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Human-readable summary",
    "details": [
      { "field": "email", "message": "Invalid format" }
    ]
  }
}
```

## Output Format

For each endpoint, produce:
1. **Method + Path** — e.g. `POST /v1/orders`
2. **Description** — one sentence on what it does
3. **Auth** — required role or token scope
4. **Request** — headers, path params, query params, body schema
5. **Responses** — all possible status codes with payload shapes
6. **Notes** — idempotency key, rate limits, deprecation warnings if any