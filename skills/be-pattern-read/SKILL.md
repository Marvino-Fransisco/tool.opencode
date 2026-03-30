---
name: be-pattern-read
description: Use this skill when the agent needs to understand the architectural and coding patterns of an existing project before designing a new feature. Triggers include: any request to read the project structure, identify patterns, or understand how the codebase is organized. Also use at the start of every design task before producing any design output — the agent must know the project's patterns to follow them.
---

This skill guides the systematic reading of an existing project's codebase to extract its architectural patterns, conventions, and design decisions.

The user provides access to a project directory. The goal is to understand the project well enough to design new features that fit naturally into it — no friction, no pattern violations.

## Reading Strategy

Do not read every file. Read strategically:

### Step 1 — Get the tree
```bash
find . -type f \( -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" -o -name "*.java" \) \
  | grep -v node_modules \
  | grep -v dist \
  | grep -v .git \
  | head -80
```
This gives a structural overview without noise. Look for folder names — they reveal the architecture style.

### Step 2 — Identify the architecture style
Look for these folder patterns:

| Folders found | Architecture style |
|---|---|
| `controllers/`, `services/`, `repositories/` | Layered / MVC |
| `domain/`, `application/`, `infrastructure/` | Clean / Hexagonal |
| `modules/users/`, `modules/orders/` | Feature-based / Modular |
| `handlers/`, `middleware/`, `routes/` | Express-style flat |
| `cmd/`, `internal/`, `pkg/` | Go standard layout |
| `resolvers/`, `schema/`, `dataloaders/` | GraphQL-first |

### Step 3 — Read representative files
Pick one complete feature (e.g., "users" or "auth") and read all its layers:
- Route/controller definition
- Service/use-case layer
- Repository/data-access layer
- Model/entity definition
- DTO / request validation schema
- Tests (unit + integration if present)

### Step 4 — Extract conventions
While reading, extract answers to:

**Naming**
- How are files named? `camelCase.ts`, `kebab-case.ts`, `snake_case.py`?
- How are classes/functions named? `UserService`, `user_service`, `useUser`?
- How are endpoints named? `/users`, `/user`, `/api/v1/users`?

**Error handling**
- Does the project use a custom error class? What fields does it have?
- Are errors thrown and caught by middleware, or returned explicitly?
- What is the error response envelope shape?

**Validation**
- Where is input validated? Controller layer, service layer, middleware?
- What library is used? `zod`, `joi`, `class-validator`, `pydantic`, `express-validator`?

**Database access**
- What ORM/query builder is used? `Prisma`, `TypeORM`, `Sequelize`, `SQLAlchemy`, `GORM`, raw SQL?
- Is there a repository pattern, or are DB calls made directly in services?
- Are transactions handled explicitly? How?

**Auth**
- How is auth enforced? Middleware, decorators, guard functions?
- What is in the auth token / session? `userId`, `role`, `permissions`?

**Testing**
- What test framework? `Jest`, `Vitest`, `pytest`, `Go test`?
- Are tests colocated with source files or in a separate `tests/` folder?
- Is there a shared test helper / factory pattern?

**Response shape**
- Is there a standard response wrapper? `{ data: ..., meta: ... }` or raw payload?
- Are lists paginated? What pagination style? `{ page, limit }` vs cursor-based?

## Output Format

Produce a pattern summary with these sections:

### Architecture Style
One sentence. e.g., "This project uses a layered architecture with controllers → services → repositories."

### Folder & File Conventions
- Folder structure pattern
- File naming convention
- Test file location and naming

### Naming Conventions
- Functions, classes, variables
- API routes

### Error Handling Pattern
- Error class used
- How errors propagate
- Response envelope for errors

### Validation Pattern
- Library and location
- DTO / schema conventions

### Database Pattern
- ORM/library
- Repository pattern details
- Transaction handling

### Auth Pattern
- Enforcement mechanism
- Token/session contents

### Response Shape
- Success envelope
- Pagination style if any

### Key Dependencies
List the main libraries/frameworks with versions if visible in package.json / requirements.txt / go.mod.

### Open Questions
Things that are ambiguous or inconsistent in the codebase that the user should clarify before designing.