
with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/backend/app/models/__init__.py', 'r') as f:
    content = f.read()

# Add created_by to Plan class (after meta field)
old_plan_meta = '''    meta: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column('''

new_plan_meta = '''    meta: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column('''

content = content.replace(old_plan_meta, new_plan_meta)

# Add created_by to Task class (after meta field)
old_task_meta = '''    meta: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )'''

new_task_meta = '''    meta: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )'''

content = content.replace(old_task_meta, new_task_meta)

# Add created_by to LedgerEntry class (after meta field)
old_ledger_meta = '''    meta: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    plan: Mapped["Plan"] = relationship("Plan", back_populates="ledger_entries")'''

new_ledger_meta = '''    meta: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    plan: Mapped["Plan"] = relationship("Plan", back_populates="ledger_entries")'''

content = content.replace(old_ledger_meta, new_ledger_meta)

with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/backend/app/models/__init__.py', 'w') as f:
    f.write(content)

print('Fixed models file')

