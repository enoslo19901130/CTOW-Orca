# CTOW Architecture — v0.2.2

CTOW separates **governance state** from **execution state**.

## Execution source of truth

Orca is authoritative for:

- Run
- Task and dependency DAG
- Dispatch
- worker process/terminal
- worktree placement
- `worker_done`
- `question` / reply
- `escalation`
- heartbeat
- worker release/retention

CTOW must not mirror these into a second mutable runtime database.

## Governance source of truth

CTOW owns:

- approved project plan and revisions
- Work Package risk and acceptance criteria
- role authority
- independent review requirements
- SWARM policy
- escalation classification
- human decision requirements
- break-glass audit records

## Authority graph

```text
USER
  ↓
SOL — architecture / plan / final decisions
  ↓
TERRA — scheduling / worker placement / integration
  ↓
LUNA — assigned implementation / test / analysis
```

Full filesystem/shell access does not alter this authority graph.

## Coordination model

Sol creates the plan. Terra acts as execution coordinator and uses Orca supervised orchestration to start Luna workers. A Luna worker cannot create or reassign project workers under the normal policy.

The runtime must enforce policy at the behavioral/validation layer even though the underlying CLI has broad permissions.

## Review model

High-risk implementation requires a distinct reviewer session. Reviewer identity must differ from author identity at agent/session/dispatch level.

## Failure model

Execution failure is reported by Orca lifecycle state. Terra decides retry/reassign/escalate. Architecture-changing recovery always returns to Sol.

See the ADR directory for architecture decisions.

## Decision-state boundary

CTOW persists only governance decisions/evidence under `.ctow/`; Orca remains authoritative for execution lifecycle. `issue_fingerprint` + Decision Record prevents the same unresolved evidence bundle from recursively consuming Sol tokens. Reopening requires material evidence delta.

See `docs/adr/ADR-0002-BOUNDED-DECISION-REVALIDATION.md` for the anti-stagnation decision protocol.

## Canonical issue identity

Terra owns canonical issue identity. Luna may propose a provisional key, but Sol/Human escalations require a Terra-canonicalized fingerprint and an Issue Identity Record under `.ctow/issues/`. Fingerprint renaming requires a material change in problem identity, not wording.

## Decision progress boundary

Each issue that reaches Sol has governance progress under `.ctow/decision-progress/`: cycle count, previous escalation/decision provenance, unchanged facts, material evidence delta, and stagnation state. At cycle >=2 with the same decision question and no material delta, further targeted validation is forbidden.

See ADR-0003.
