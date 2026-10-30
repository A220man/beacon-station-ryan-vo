
with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/backend/app/api/plans.py', 'r') as f:
    content = f.read()

# Update add_ledger_entry call to pass user_id
old_call = '''    entry = await service.add_ledger_entry(
        plan_id=plan_id,
        message=data.message,
        task_id=data.task_id,
        commits_range=data.commits_range,
        test_command=data.test_command,
        test_result=test_result,
        exit_code=data.exit_code,
        tokens_used=data.tokens_used,
        meta=data.meta,
    )'''

new_call = '''    entry = await service.add_ledger_entry(
        plan_id=plan_id,
        message=data.message,
        task_id=data.task_id,
        commits_range=data.commits_range,
        test_command=data.test_command,
        test_result=test_result,
        exit_code=data.exit_code,
        tokens_used=data.tokens_used,
        meta=data.meta,
        user_id=user.id,
    )'''

content = content.replace(old_call, new_call)

with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/backend/app/api/plans.py', 'w') as f:
    f.write(content)

print('Updated add_ledger_entry call')

