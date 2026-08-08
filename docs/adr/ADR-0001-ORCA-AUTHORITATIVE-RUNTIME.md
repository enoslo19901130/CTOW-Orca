# ADR-0001 — Use Orca as the Authoritative Orchestration Runtime

- Status: Accepted
- Version: CTOW 0.2.0
- Date: 2026-08-08

## Context

CTOW v0.1 described a Python control plane that would eventually spawn Codex CLI processes, maintain Task and Issue state, manage sessions, monitor workers, create worktrees, and expose lifecycle operations through MCP.

Review identified that the code was only a skeleton and that a correct implementation would require substantial PTY, recovery, persistence, and cross-platform work.

Orca already provides the required execution primitives for supervised coding agents: worktrees, terminals, Run/Task/Dispatch state, worker start/reuse/release, completion messages, escalation, blocking questions, heartbeats, task dependencies, and coordinator inbox delivery.

## Decision

Orca is the **single authoritative execution runtime** for CTOW.

CTOW will not implement a second mutable worker/task/session lifecycle.

### Rejected as core architecture

- custom Python PTY supervisor
- custom Codex process launcher
- custom worktree manager
- custom Task/Dispatch database
- custom worker completion polling loop
- custom MCP server for worker lifecycle

### Retained in CTOW

- Sol/Terra/Luna role model
- authority matrix
- planning contract
- escalation classification
- independent review policy
- SWARM policy
- human decision policy
- break-glass policy
- schemas and validation tooling
- metrics/governance extensions that do not duplicate Orca state

## Consequences

Positive:

- less custom runtime code;
- Orca UI directly reflects workers/worktrees;
- built-in lifecycle and recovery semantics;
- cross-platform behavior delegated to Orca;
- no dual execution source of truth.

Tradeoffs:

- CTOW depends on Orca orchestration behavior and CLI compatibility;
- orchestration experimental feature must be enabled where required;
- runtime integration tests need a running Orca instance;
- model/effort launch support must be verified against the installed Orca/Codex versions.

## Rule for future agents

Do not reintroduce a custom execution supervisor merely because a Python wrapper appears easier. A replacement requires a new ADR documenting which Orca primitive is insufficient and why.
