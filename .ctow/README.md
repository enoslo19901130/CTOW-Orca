# `.ctow/` Governance Evidence

This directory stores **CTOW governance evidence only**. Orca remains the authoritative source for execution state such as Runs, Tasks, Dispatches, terminals, worktrees, worker lifecycle, completion, and messaging.

- `plans/` — approved Sol plans and revisions.
- `issues/` — Terra-owned canonical issue identity records and aliases.
- `escalations/` — compressed escalation briefs/evidence.
- `decisions/` — Sol/Human Decision Records.
- `decision-progress/` — per-fingerprint cycle/stagnation ledgers.
- `reviews/` — independent review reports.
- `human-decisions/` — blocking owner decisions.
- `audits/break-glass/` — audited authority bypass records.

Do **not** create a shadow Task/Dispatch/session database here. If a governance file references an Orca Task or Dispatch, it stores only provenance/evidence, not a mirrored runtime state.
