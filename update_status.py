with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/STATUS.md', 'r') as f:
    content = f.read()

new_content = """# Checkpoint status

Work in progress; not a release-readiness or successful QA claim.

Version: 1.1.0

## Completed this round

- Added `created_by` field to Plan, Task, and LedgerEntry models for ownership tracking
- Updated PlanService to populate `created_by` on create operations
- Updated API responses to include `created_by` field
- Updated frontend TypeScript types to include `created_by`
- All backend tests pass (19/19)
- All frontend tests pass (4/4)
- Frontend typecheck and build pass
- Docker Compose config validates

## Outstanding findings

No completed independent review for this checkpoint.

## Next round

Resume PLAN.md, check the current code, fix failures and advance one feature.
"""

with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/STATUS.md', 'w') as f:
    f.write(new_content)

print('Updated STATUS.md')
