# opencode

My Opencode configuration — custom agents, skills, and MCP integrations.

## Directory Structure

```
.
├── opencode.jsonc          # Opencode runtime config (MCP servers, permissions, tool access)
├── package.json            # Node dependencies (@opencode-ai/plugin)
├── agents/                 # Custom agent definitions
├── skills/                 # Reusable skill prompts
└── node_modules/           # Installed dependencies (gitignored)
```

## Agents

Custom agents defined in `agents/`. Each agent has a frontmatter config (model, temperature, mode, tools) and a system prompt.

| Agent | Mode | Description |
|---|---|---|
| `backend-designer` | primary | API design, architecture, optimization, scalability |
| `data-designer` | primary | Data modeling, pipelines, analytics, governance |
| `frontend-designer` | primary | UI, code, optimization, scalability |
| `notion` | subagent | Notion CRUD via MCP — pages, databases, search |
| `discord` | subagent | Discord messaging via MCP — send, edit, delete, upload |
| `market-analyzer` | subagent | Crypto market analysis (Bybit) — Auction Market Theory, Volume Profile, VSA |

## Skills

Reusable prompt templates in `skills/`. Each skill lives in its own folder with a `SKILL.md` defining triggers and instructions. Skills are prefixed by domain:

### Backend (`be-`)

| Skill | Purpose |
|---|---|
| `be-api-contract-design` | Design/review REST or GraphQL API endpoints |
| `be-async-queue-plan` | Plan async queue architectures |
| `be-auth-authz-design` | Design authentication & authorization flows |
| `be-data-schema-design` | Design database schemas |
| `be-dependency-risk-analysis` | Analyze dependency risks |
| `be-idempotency-edge-case-plan` | Plan for idempotency & edge cases |
| `be-observability-plan` | Plan observability (logging, metrics, tracing) |
| `be-pattern-read` | Read and understand backend patterns |
| `be-query-optimization` | Optimize database queries |
| `be-system-flow-diagram` | Generate system flow diagrams |

### Frontend (`fe-`)

| Skill | Purpose |
|---|---|
| `fe-a11y-check` | Accessibility auditing |
| `fe-component-design` | Component structure & props design |
| `fe-diagram-generation` | Generate diagrams for frontend flows |
| `fe-docs-read` | Read project documentation |
| `fe-edge-case-generation` | Generate edge case scenarios |
| `fe-markdown-format` | Markdown formatting |
| `fe-pattern-detection` | Detect existing patterns in codebase |
| `fe-perf-advice` | Frontend performance advice |
| `fe-project-read` | Read and understand project structure |
| `fe-request-analysis` | Analyze feature requests |
| `fe-state-design` | State management design |
| `fe-tradeoff-advice` | Tradeoff analysis |
| `fe-ux-feedback-design` | UX feedback design |

### Utilities

| Skill | Purpose |
|---|---|
| `matplotlib` | Low-level plotting with full customization |
| `pdf` | PDF processing — read, merge, split, watermark, forms, OCR |

## Configuration (`opencode.jsonc`)

- **MCP servers**: Notion (enabled), Discord (disabled), Market Analyzer (disabled) — all run via Docker
- **Permissions**: Skills are denied by default (`"*"  : "deny"`)
- **Tool access**: MCP tools disabled globally, enabled per-agent
