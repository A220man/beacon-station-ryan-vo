
with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/backend/app/services/plan_service.py', 'r') as f:
    content = f.read()

# Update add_task to add created_by=user_id
old_add_task = '''        task = Task(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            sequence=sequence,
            title=title,
            description=description,
            file_path=task_path,
            estimated_tokens=self._estimate_tokens(description or ""),
        )'''

new_add_task = '''        task = Task(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            sequence=sequence,
            title=title,
            description=description,
            file_path=task_path,
            estimated_tokens=self._estimate_tokens(description or ""),
            created_by=user_id,
        )'''

content = content.replace(old_add_task, new_add_task)

# Update add_ledger_entry to add user_id parameter and created_by
old_ledger_sig = '''    async def add_ledger_entry(
        self,
        plan_id: str,
        message: str,
        task_id: Optional[str] = None,
        commits_range: Optional[str] = None,
        test_command: Optional[str] = None,
        test_result: Optional[str] = None,
        exit_code: Optional[int] = None,
        tokens_used: int = 0,
        meta: Optional[dict] = None,
    ) -> LedgerEntry:'''

new_ledger_sig = '''    async def add_ledger_entry(
        self,
        plan_id: str,
        message: str,
        task_id: Optional[str] = None,
        commits_range: Optional[str] = None,
        test_command: Optional[str] = None,
        test_result: Optional[str] = None,
        exit_code: Optional[int] = None,
        tokens_used: int = 0,
        meta: Optional[dict] = None,
        user_id: Optional[str] = None,
    ) -> LedgerEntry:'''

content = content.replace(old_ledger_sig, new_ledger_sig)

old_ledger_entry = '''        entry = LedgerEntry(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            task_id=task_id,
            sequence=sequence,
            message=message,
            commits_range=commits_range,
            test_command=test_command,
            test_result=test_result,
            exit_code=exit_code,
            tokens_used=tokens_used,
            meta=meta or {},
        )'''

new_ledger_entry = '''        entry = LedgerEntry(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            task_id=task_id,
            sequence=sequence,
            message=message,
            commits_range=commits_range,
            test_command=test_command,
            test_result=test_result,
            exit_code=exit_code,
            tokens_used=tokens_used,
            meta=meta or {},
            created_by=user_id,
        )'''

content = content.replace(old_ledger_entry, new_ledger_entry)

with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/backend/app/services/plan_service.py', 'w') as f:
    f.write(content)

print('Updated add_task and add_ledger_entry')

