with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/CHANGELOG.md', 'r') as f:
    content = f.read()

# Add entry for this checkpoint
new_entry = """## 1.1.0 — work-in-progress checkpoint

### Added
- `created_by` field on Plan, Task, and LedgerEntry models for ownership tracking
- API responses now include `created_by` field
- Frontend types updated with `created_by` field
- Service layer populates `created_by` from authenticated user context

### Changed
- Plan, Task, and LedgerEntry SQLAlchemy models extended with optional `created_by` column
- PlanService.create_plan, add_task, add_ledger_entry accept and store `user_id`
- PlanResponse, TaskResponse, LedgerEntryResponse include `created_by` field

### Security
- No hardcoded secrets; all credentials via environment variables
- Frontend tokens in memory only, no localStorage persistence

### Known Limitations
- SQLite only; PostgreSQL recommended for production
- Agent Teams orchestration API stubbed; requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
- LLM integration adapters not yet implemented (planned)
- Single-user demo credentials in Keycloak realm export

"""

# Insert after the first "## " header
lines = content.split('\n')
# Find the first "## " line and insert after it
for i, line in enumerate(lines):
    if line.startswith('## ') and '1.1.0' in line:
        # Insert after this section
        # Find the next "## " or end
        insert_idx = i + 1
        while insert_idx < len(lines) and not lines[insert_idx].startswith('## '):
            insert_idx += 1
        lines = lines[:insert_idx] + new_entry.split('\n') + lines[insert_idx:]
        break

with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/CHANGELOG.md', 'w') as f:
    f.write('\n'.join(lines))

print('Updated CHANGELOG.md')
