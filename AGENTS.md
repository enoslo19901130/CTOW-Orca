# AGENTS.md — CTOW Repository Entry Point

This repository is CTOW: Codex Team Orchestration Workflow.

Before changing implementation or policy:

1. Read `README.md`.
2. Read `docs/adr/ADR-0001-ORCA-AUTHORITATIVE-RUNTIME.md`.
3. Read `config/agents.yaml` and `config/policy.yaml`.
4. Read the Skill matching your assigned role under `.agents/skills/`.
5. Do not implement a custom worker/PTY/task runtime unless a new ADR explicitly supersedes ADR-0001.

Core invariant:

> Orca owns execution lifecycle. CTOW owns governance.

Role hierarchy:

```text
USER → SOL → TERRA → LUNA
```

Escalation reverses that direction.

Terminology is **Worker** throughout this repository.

## Mandatory decision-loop rule (v0.2.2)

When an issue escalates, preserve its `issue_fingerprint`. Terra owns canonical issue identity and must consult `.ctow/issues/`, `.ctow/decisions/`, and `.ctow/decision-progress/` and send Sol a compressed Decision Brief. A Sol-decided issue cannot be reopened without material evidence delta, failed acceptance after applying the decision, or the result of one bounded targeted validation. Never spend repeated MAX reasoning on the same evidence path.

Before changing anti-stagnation behavior, read ADR-0002 and ADR-0003. Rewording, repeated confirmation, or another agreeing worker is not a material evidence delta.
