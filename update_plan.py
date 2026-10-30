
with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/PLAN.md', 'r') as f:
    content = f.read()

# Update core-infrastructure status to done
content = content.replace(
    '''### core-infrastructure — Core Infrastructure: FastAPI backend, React frontend, Docker, CI

Status: in_progress

Acceptance:
- FastAPI app starts and serves health endpoint
- React + TypeScript + Vite frontend builds and serves
- Docker Compose brings up backend, frontend, Keycloak, PostgreSQL
- CI workflow runs backend tests, frontend typecheck/build/test
- README with install/run/test steps
- portfolio.json at root with correct schema''',
    '''### core-infrastructure — Core Infrastructure: FastAPI backend, React frontend, Docker, CI

Status: done

Acceptance:
- FastAPI app starts and serves health endpoint
- React + TypeScript + Vite frontend builds and serves
- Docker Compose brings up backend, frontend, Keycloak, PostgreSQL
- CI workflow runs backend tests, frontend typecheck/build/test
- README with install/run/test steps
- portfolio.json at root with correct schema

Implementation:
- backend/app/main.py
- backend/app/core/config.py
- backend/app/core/database.py
- backend/app/core/auth.py
- backend/app/api/health.py
- backend/app/api/plans.py
- backend/app/models/__init__.py
- backend/app/services/plan_service.py
- backend/app/services/test_parser.py
- frontend/src/App.tsx
- frontend/src/api/client.ts
- frontend/src/types/index.ts
- frontend/src/pages/*.tsx
- compose.yaml
- .github/workflows/ci.yml

Tests:
- backend/tests/test_health.py
- frontend/src/App.test.tsx''')

with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/PLAN.md', 'w') as f:
    f.write(content)

print('Updated PLAN.md')

