# Task Contract and Work-Package Mapping

> **Compatibility notice:** Orca CLI examples in CTOW are version-sensitive. Treat installed Orca help and the installed orchestration skill as authoritative.

A Sol Work Package (WP) is a governance unit. An Orca Task is an execution unit. They are intentionally not one-to-one.

```text
Work Package
 ├─ 1..N execution Tasks
 ├─ 0..N targeted-validation Tasks
 ├─ 0..N SWARM investigation Tasks
 └─ 0..N independent review Tasks
```

## Task types

- `execution` — implementation/research/test required to satisfy the WP.
- `review` — independent review of a named execution task; always a separate Task + Dispatch.
- `targeted_validation` — one bounded experiment requested by Sol; research/test only, never open-ended.
- `swarm_investigation` — independent research task used during SWARM before Terra synthesis.

## Mapping rules

- Terra may split one WP into multiple Orca Tasks when scopes can be isolated or dependencies expressed explicitly.
- High/critical-risk execution tasks require `independent_review_required: true`.
- Independent review uses a distinct reviewer agent/session/dispatch and `review_of_task_id`.
- A targeted-validation task must preserve Sol's exact hypothesis/method/stop criteria; Terra/Luna may not broaden it.
- Terra owns the governance Task Contract; Orca owns actual Task/Dispatch runtime state.

See `examples/TASK-WP001.yaml`, `examples/TASK-REVIEW-WP002.yaml`, and `schemas/task-contract.schema.json`.
