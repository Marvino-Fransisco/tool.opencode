---
name: be-auth-authz-design
description: Use this skill when the user needs to design authentication or authorization for a backend feature. Triggers include: designing a login flow, defining who can access what, planning RBAC or ABAC rules, designing JWT/session strategy, or reviewing permissions for an endpoint. Also use when the user asks "who can call this endpoint", "how should I protect this route", "design the auth for X", or "what roles do I need".
---

This skill guides the design of secure, correct, and maintainable authentication (AuthN) and authorization (AuthZ) for backend features.

The user provides a feature or set of endpoints. They may include context about the user model, existing auth system, or business rules around access.

## Core Distinction

- **Authentication (AuthN)**: "Who are you?" — verifying identity (login, token validation)
- **Authorization (AuthZ)**: "What can you do?" — verifying permissions (role checks, ownership checks, policy rules)

Design them separately. AuthN is usually solved once per project. AuthZ is designed per feature.

## Authentication Design

### Token Strategy
Choose one and apply it consistently:

| Strategy | When to use |
|---|---|
| **JWT (stateless)** | Microservices, horizontal scaling, short-lived sessions |
| **Opaque token + session store** | When you need instant revocation (logout, ban) |
| **OAuth2 / OIDC** | Third-party login, delegated access, enterprise SSO |
| **API Key** | Service-to-service, developer APIs, long-lived programmatic access |

### JWT Design
If using JWTs:
- **Payload** — include only what's needed: `sub` (userId), `role`, `iat`, `exp`; avoid PII
- **Expiry** — short-lived access tokens (15min–1hr) + longer refresh tokens (7–30 days)
- **Algorithm** — use `RS256` (asymmetric) for multi-service setups; `HS256` is fine for single-service
- **Refresh flow** — define the refresh endpoint and rotation strategy (rotate on use vs fixed)
- **Revocation** — JWTs can't be invalidated before expiry; use a blocklist in Redis for logout/ban if needed

### Token Delivery
- Access token in `Authorization: Bearer <token>` header — never in query params
- Refresh token in `HttpOnly Secure SameSite=Strict` cookie — never in localStorage

### Login Flow
Define:
1. Credential submission (email+password, OAuth code, etc.)
2. Identity verification
3. Token issuance (access + refresh)
4. Failure handling (invalid credentials, account locked, unverified email)
5. Logout / token invalidation

## Authorization Design

### Choose the right model

| Model | When to use |
|---|---|
| **RBAC** (Role-Based Access Control) | Clear, stable roles like `admin`, `editor`, `viewer` |
| **ABAC** (Attribute-Based Access Control) | Fine-grained rules based on resource attributes and user attributes |
| **Ownership-based** | User can only access their own resources |
| **Hybrid** | RBAC for coarse access + ownership for row-level access |

### RBAC Design
Define:
- **Roles** — name and description for each role
- **Permissions** — list of actions (e.g., `orders:read`, `orders:write`, `orders:delete`)
- **Role-permission matrix** — which roles have which permissions
- **Role assignment** — how roles are assigned and changed

Example matrix:
| Permission | Admin | Manager | Customer |
|---|---|---|---|
| `orders:read:all` | ✅ | ✅ | ❌ |
| `orders:read:own` | ✅ | ✅ | ✅ |
| `orders:write` | ✅ | ✅ | ✅ |
| `orders:delete` | ✅ | ❌ | ❌ |

### Ownership Checks
For any resource a user creates, enforce:
1. Does the requesting user own this resource? (check `resource.user_id === token.sub`)
2. Or does the user have an admin/override role that bypasses ownership?

Never rely on the client to send the owner ID — derive it from the token.

### Enforcement Layer
Define where authorization is checked:
- **Middleware/guard** — for coarse role checks before the handler runs
- **Service layer** — for ownership and attribute checks after fetching the resource
- **Database layer** — for row-level security (PostgreSQL RLS) as a last line of defense

**Never** do authorization checks in the controller only — the service layer must also enforce it.

## Output Format

### Authentication Design
- Token strategy and rationale
- JWT payload structure (if JWT)
- Token expiry and refresh strategy
- Login flow (step by step)
- Logout / revocation strategy

### Authorization Design
- Access control model (RBAC / ABAC / ownership)
- Role definitions
- Permission list
- Role-permission matrix
- Ownership rules (if any)
- Enforcement points (middleware / service / DB)

### Endpoint-level Auth Requirements
For each endpoint in the feature:
| Endpoint | AuthN required | Minimum role | Ownership check | Notes |
|---|---|---|---|---|
| `GET /orders` | Yes | Manager | No — sees all | Admin sees all |
| `GET /orders/:id` | Yes | Customer | Yes — own orders | Manager can see any |
| `DELETE /orders/:id` | Yes | Admin | No | Soft delete only |

### Security Considerations
- Token leakage risks and mitigations
- Privilege escalation risks
- Missing permission gaps (endpoints not yet covered)
- Audit logging requirements (who did what to which resource)