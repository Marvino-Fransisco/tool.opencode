---
name: be-system-flow-diagram
description: Use this skill when the user needs a diagram to visualize system behavior or architecture. Triggers include: drawing a sequence diagram, entity-relationship diagram (ERD), architecture diagram, data flow diagram, or state machine. Also use when the user says "diagram this", "show the flow for X", "draw the architecture", "visualize how X works", or when a design doc needs diagrams to be readable.
---

This skill guides the creation of clear, accurate, and useful technical diagrams for backend systems using Mermaid or PlantUML syntax.

The user provides a system, feature, or flow to visualize. They may include existing code, a design description, or just a high-level idea.

## Design Thinking

Before drawing, choose the right diagram type for the story being told:
- **Sequence diagram** — for showing how services/components communicate over time (request/response, async events)
- **ERD** — for showing data models and their relationships
- **Architecture diagram** — for showing system components, their boundaries, and how they connect
- **Flowchart** — for showing decision logic, process steps, or branching paths
- **State machine** — for showing how an entity transitions between states

Then produce a diagram that is:
- Focused on one concern per diagram — don't mix architecture and sequence in one
- Accurate to the actual system, not idealized
- Readable at a glance — label every arrow, name every component clearly

## Diagram Guidelines

### Sequence Diagrams (Mermaid)
Use for: API calls, service-to-service flows, async job processing, auth flows.

```mermaid
sequenceDiagram
    actor User
    participant API
    participant AuthService
    participant DB

    User->>API: POST /login {email, password}
    API->>AuthService: validate(email, password)
    AuthService->>DB: SELECT user WHERE email = ?
    DB-->>AuthService: user row
    AuthService-->>API: {valid: true, userId}
    API-->>User: 200 {token}
```

Rules:
- Use `actor` for humans, `participant` for services/systems
- Solid arrow `->>`  for requests, dashed `-->>`  for responses
- Use `alt`/`else` blocks for branching (success vs error)
- Include error paths — not just the happy path

### ERD (Mermaid)
Use for: data modeling, schema reviews, relationship visualization.

```mermaid
erDiagram
    USER {
        uuid id PK
        text email
        timestamptz created_at
    }
    ORDER {
        uuid id PK
        uuid user_id FK
        text status
        numeric total
        timestamptz created_at
    }
    USER ||--o{ ORDER : "places"
```

Rules:
- Always include PK and FK annotations
- Use relationship labels that read naturally: `"places"`, `"belongs to"`, `"contains"`
- Include the most important columns only — not every field

### Architecture Diagrams (Mermaid flowchart)
Use for: system overview, component boundaries, deployment topology.

```mermaid
flowchart TD
    Client["Client (Browser/Mobile)"]
    Gateway["API Gateway"]
    AuthSvc["Auth Service"]
    OrderSvc["Order Service"]
    DB[("PostgreSQL")]
    Cache[("Redis")]
    Queue["Message Queue (SQS)"]
    Worker["Background Worker"]

    Client --> Gateway
    Gateway --> AuthSvc
    Gateway --> OrderSvc
    OrderSvc --> DB
    OrderSvc --> Cache
    OrderSvc --> Queue
    Queue --> Worker
    Worker --> DB
```

Rules:
- Group related components visually using subgraphs
- Use consistent node shapes: rectangles for services, cylinders `[(" ")]` for datastores, parallelograms for queues
- Label every edge with the protocol or action: `HTTP`, `SQL`, `publishes`, `consumes`

### State Machine (Mermaid stateDiagram)
Use for: order lifecycle, payment status, job status, approval workflows.

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Processing : payment confirmed
    Processing --> Shipped : fulfillment complete
    Shipped --> Delivered : delivery confirmed
    Processing --> Failed : fulfillment error
    Failed --> [*]
    Delivered --> [*]
```

Rules:
- Every state should have at least one outbound transition (except terminal states)
- Label every transition with the event or condition that triggers it
- Include error/failure states — they're often the most important

## Output Format

For each diagram:
1. **Diagram type** and rationale for choosing it
2. **Mermaid/PlantUML code block** — ready to paste and render
3. **Narrative walkthrough** — 3–5 sentences explaining what the diagram shows
4. **Key decisions visible in the diagram** — e.g., "Auth is a separate service", "DB writes go through a queue"
5. **What's intentionally omitted** — to keep the diagram focused