# ADR-0004 — Add Thin CTOW Command Entry Points

- Status: Accepted
- Version: CTOW 0.2.2
- Date: 2026-08-08

## Context

CTOW documents a User → Sol → Terra → Luna workflow, but v0.2.2 originally exposed only `ctow-guard` validation commands. Users needed memorable entry points for planning intake and starting an approved execution without copying orchestration syntax manually.

A convenience CLI could accidentally become a second runtime by launching Workers, mirroring Task state, polling terminals, or treating an unreviewed goal as an approved Plan. That would violate ADR-0001.

## Decision

CTOW provides:

- `ctow plan` and `ctow-plan` to record a planning request and generate a Sol-ready prompt;
- `ctow start` and `ctow-start` to validate an approved Plan and create its Orca Run;
- `ctow status` and `ctow-status` to combine read-only Orca status with local governance artifacts;
- `--dry-run` to validate and reveal the intended Orca mutation without executing it.

`ctow-plan` does not generate or approve architecture. `ctow-start` does not start Luna, schedule Tasks, monitor Workers, or persist mutable Orca state. After Run creation, Terra remains responsible for Task DAG creation and supervised Dispatch through the installed Orca orchestration contract.

The positional `ctow-start "<goal>"` form resolves only an exactly matching, valid Plan under `.ctow/plans/`. It never treats the goal string itself as approval.

## Consequences

Positive:

- a memorable and scriptable project entry point;
- Plan-first enforcement before execution state is created;
- Orca receipts remain the execution source of truth;
- failure and dry-run behavior can be unit tested without an Orca mutation.

Tradeoffs:

- a Human or Sol session must still perform real planning;
- Terra orchestration remains a separate governed phase;
- CLI compatibility continues to depend on the installed Orca binary.

## Explicit non-goals

- custom agent/process launcher;
- automatic AI Plan generation inside the Python package;
- CTOW-owned Run, Task, Dispatch, terminal, or Worker state;
- implicit retries after an unknown Orca mutation result.
