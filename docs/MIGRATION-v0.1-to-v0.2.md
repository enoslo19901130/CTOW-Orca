# Migration from CTOW v0.1.x to v0.2.0

## Removed direction

v0.1 contained a skeleton for:

- Python `mcp_server.py` worker lifecycle;
- custom service/task state;
- custom Codex adapter/spawn intent;
- custom issue state storage.

Those components are intentionally removed as the primary architecture.

## Replacement

Execution lifecycle is delegated to Orca orchestration. CTOW retains only governance validation and role skills.

## Why

A custom supervisor would duplicate Orca's worktrees, terminals, Tasks, Dispatches, worker completion, escalation, and recovery semantics, creating two sources of truth.
