# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — 2026-10-22

### Added
- FastAPI backend with SQLite persistence (SQLAlchemy async)
- React + TypeScript + Vite frontend with dashboard, plan management, task execution, ledger views
- Plan CRUD with split markdown storage (overview.md + tasks/task-XXX.md)
- Task management with status transitions (pending → in_progress → completed/failed)
- Execution ledger with test result parsing for node --test, pytest, jest, vitest, cargo test, go test
- Token estimation for plans and tasks
- OIDC authentication via Keycloak (PKCE, HttpOnly cookies, role-based access)
- Docker Compose with backend, frontend, Keycloak, persistent volumes
- CI workflow (backend tests, frontend typecheck/build/test, Docker builds)
- Comprehensive README with architecture diagram, API reference, deployment docs
- MIT License

### Security
- Demo mode for local development (refused in production)
- No hardcoded secrets; all credentials via environment variables
- Frontend tokens in memory only, no localStorage persistence

### Known Limitations
- SQLite only; PostgreSQL recommended for production
- Agent Teams orchestration API stubbed; requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
- LLM integration adapters not yet implemented (planned)
- Single-user demo credentials in Keycloak realm export