# CTOW Workflow

## Phase 0 — Request intake

Human supplies project objective, constraints, and any explicit acceptance requirements to Sol.

## Phase 1 — Sol planning

Sol operates as Architect:

- inspect repository and constraints;
- produce plan revision;
- define Work Packages;
- define dependencies;
- define risk;
- define acceptance criteria;
- recommend worker count/profile;
- identify mandatory review points.

Sol does not micro-schedule Luna workers.

## Phase 2 — Terra execution setup

Terra receives an approved plan and becomes execution coordinator.

Terra:

- creates/binds an Orca execution Run;
- creates Tasks from ready Work Packages;
- expresses dependencies in Orca Task DAG;
- chooses worktree placement;
- chooses actual Luna allocation within policy capacity;
- starts all independent workers before waiting.

## Phase 3 — Luna execution

Each Luna receives a bounded Task Contract and works only inside its assigned objective. It may inspect the full repository, but should not silently broaden the implementation scope.

A worker reports one of:

- `worker_done` — succeeded/failed with evidence;
- `question` — blocking clarification;
- `escalation` — issue beyond worker authority;
- heartbeat/status for long-running progress.

## Phase 4 — Terra supervision loop

Terra waits for actionable Orca deliveries and processes every item before acknowledgement.

Terra does not treat a timeout as worker failure.

On `question`: answer if within execution authority, otherwise escalate to Sol.

On `escalation`: canonicalize/reuse issue identity, consult decision/progress history, resolve within execution authority, or escalate a compressed Decision Brief to Sol.

On `worker_done`: inspect result, tests, diff, and policy requirements; release/reuse worker appropriately.

## Phase 5 — Independent review

For high-risk work, Terra dispatches a distinct Luna reviewer session. Reviewer receives minimal non-anchoring evidence first.

Failed review routes correction back to a worker. Architecture-level findings route to Sol.

## Phase 6 — Integration

Terra owns integration sequencing and merge conflict resolution. Break-glass modifications by Terra must be audited if they exceed ordinary integration repair.

## Phase 7 — Sol final review

Sol checks delivery against plan, architecture, unresolved escalations, and acceptance criteria.

If plan assumptions changed, Sol revises the plan before additional execution.

## Phase 8 — Human completion / decision

Human receives completion summary or a decision gate when human authority is required.

## Anti-stagnation overlay

At every escalation boundary, preserve evidence but compress context. Terra deduplicates identical findings and checks decision history before escalating to Sol. Sol does not restart open-ended investigation. A blocking escalation must end in a decision, one bounded targeted validation, a plan revision, or a Human gate.

The same canonical issue fingerprint may not bounce Luna → Terra → Sol repeatedly without typed material evidence delta. Terra owns canonicalization and updates a Decision Progress Ledger. At cycle 2 or later, the same decision question with no material delta is stagnation; further targeted validation is forbidden.
