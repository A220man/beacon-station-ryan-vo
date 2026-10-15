# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-infrastructure

## Roadmap

### core-infrastructure — Core Infrastructure: FastAPI backend, React frontend, Docker, CI

Status: in_progress

Acceptance:
- FastAPI app starts and serves health endpoint
- React + TypeScript + Vite frontend builds and serves
- Docker Compose brings up backend, frontend, Keycloak, PostgreSQL
- CI workflow runs backend tests, frontend typecheck/build/test
- README with install/run/test steps
- portfolio.json at root with correct schema

### auth-oidc — OIDC Authentication with Keycloak

Status: planned

Acceptance:
- Backend validates JWT tokens from Keycloak
- Frontend implements PKCE login flow
- Protected API endpoints reject unauthenticated requests
- Role-based access control (viewer/operator/admin)
- Logout clears session

### plan-management — Plan Management: CRUD, persistence, token-efficient storage

Status: planned

Acceptance:
- Create/read/update/delete plans via API
- Plans stored as split markdown files (overview + per-task)
- SQLite persistence with pagination/filtering
- Token usage estimation endpoint

### task-execution-engine — Task Execution Engine: subagent dispatch, ledger, test result parsing

Status: planned

Acceptance:
- Task start/done API with git commit tracking
- Ledger records test results (parses pass/fail from common runners)
- Subagent dispatch simulation with focused prompts
- Exit code + summary extraction for node --test, pytest, npm test

### agent-teams-support — Agent Teams Support: detection, orchestration, teammate coordination

Status: planned

Acceptance:
- Detects Agent Teams availability (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS)
- Team creation, teammate spawning, task assignment APIs
- Plan approval workflow (review/approve/reject)
- Graceful shutdown coordination

### llm-integration — LLM Integration: multi-provider adapters, opt-in explanations

Status: planned

Acceptance:
- OpenAI-compatible, Anthropic, Gemini, Ollama adapters
- Configurable via LLM_PROVIDER, LLM_MODEL, LLM_BASE_URL
- Opt-in advisory explanations grounded in records
- Bounded timeouts, redacted errors, no hardcoded keys

### dashboard-ui — Domain Dashboard: plans, tasks, execution, teams, token analytics

Status: planned

Acceptance:
- Plan list with create/edit/detail views
- Task execution monitoring with ledger display
- Token usage analytics per plan/task
- Agent Teams orchestration panel
- Loading/error/empty states throughout

