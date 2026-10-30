
import re

with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/backend/app/services/plan_service.py', 'r') as f:
    content = f.read()

# Update create_plan to add created_by=user_id to Plan
old_plan = '''        plan = Plan(
            id=plan_id,
            name=name,
            description=description,
            execution_mode=execution_mode,
            overview_path=overview_path,
            tasks_dir=tasks_dir,
            estimated_tokens=estimated_tokens,
        )'''

new_plan = '''        plan = Plan(
            id=plan_id,
            name=name,
            description=description,
            execution_mode=execution_mode,
            overview_path=overview_path,
            tasks_dir=tasks_dir,
            estimated_tokens=estimated_tokens,
            created_by=user_id,
        )'''

content = content.replace(old_plan, new_plan)

# Update create_plan to add created_by=user_id to Task (initial tasks)
old_task = '''            task = Task(
                id=str(uuid.uuid4()),
                plan_id=plan_id,
                sequence=seq,
                title=title,
                description=desc,
                file_path=path,
                estimated_tokens=self._estimate_tokens(desc or ""),
            )'''

new_task = '''            task = Task(
                id=str(uuid.uuid4()),
                plan_id=plan_id,
                sequence=seq,
                title=title,
                description=desc,
                file_path=path,
                estimated_tokens=self._estimate_tokens(desc or ""),
                created_by=user_id,
            )'''

content = content.replace(old_task, new_task)

with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/backend/app/services/plan_service.py', 'w') as f:
    f.write(content)

print('Updated create_plan')

