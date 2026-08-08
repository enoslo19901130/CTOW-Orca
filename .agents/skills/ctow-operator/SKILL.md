---
name: ctow-operator
description: Operate CTOW project entry points for planning intake, approved-Plan startup, and read-only status. Use when the user asks to start, plan, inspect, query status, resume, or choose the next action in a CTOW/Orca-governed repository, or mentions ctow, ctow-plan, ctow-start, or ctow-status.
---

# CTOW Operator

Use the installed CTOW CLI as the interface and Orca as the execution source of truth.

## Choose the action

- Status or progress question: run `ctow status` first.
- New goal requiring planning: run `ctow-plan "<goal>"`.
- Start an approved Plan: preview with `ctow-start --plan <path> --dry-run`; execute without `--dry-run` only when the user asked to start.
- Exact-goal startup: use `ctow-start "<goal>"` only when one validated Plan under `.ctow/plans/` has that exact goal.
- Schema or policy validation: continue using `ctow-guard`.

## Status interpretation

`ctow status` returns JSON combining:

- Orca runtime readiness;
- the current coordinator-bound Run;
- available Orca Runs;
- local planning requests;
- valid and invalid approved Plans.

Treat Orca receipts as authoritative for Run, Task, Dispatch, Worker, terminal, and worktree state. Treat `.ctow/` only as governance evidence. Never infer completion from a timeout or mirror execution state into CTOW files.

## Safety boundary

Do not start execution from a goal string that lacks an approved Plan. Do not launch Luna directly, invent Task state, or add a custom worker/process supervisor. After `ctow-start` creates a Run, Terra owns Task DAG creation and supervised Dispatch through the installed Orca orchestration contract.

If the command is unavailable inside the repository, use `python -m ctow_guard.workflow_cli <subcommand>` as a diagnostic fallback and report that the package entry points need installation.

`ctow-start --dry-run` is also the required Terra runtime-policy handoff: its
`terra_launch` receipt contains the centrally compiled Codex argv plus
requested/expected policy. A real start is not execution-started until Orca
returns a verifiable effective model, effort, `fast_mode: false`, sandbox, and
approval receipt from one explicit effective subtree returned by Orca. Missing
or mismatched effective policy is a typed fail-closed error, even if Orca
created a Run. Do not manually launch a second Codex process or treat
`auto_approve` as permission to bypass CTOW Human gates.
