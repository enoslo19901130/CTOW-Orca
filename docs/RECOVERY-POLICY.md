# Recovery Policy

Orca owns execution lifecycle recovery. CTOW defines decision policy around the runtime result.

## Worker timeout

A coordinator wait timeout is not worker failure. Continue bounded waits while worker lifecycle/terminal evidence indicates the worker remains alive.

## Worker failure

Terra may retry or reassign when failure remains within the approved plan. Repeated failure or evidence of plan infeasibility escalates to Sol.

## Worker/session crash

Use Orca's current worker/terminal inspection and recovery primitives. Do not create a second CTOW PID watchdog.

## Worktree conflict

Terra owns placement. Resolve merge/scope conflicts at the commander level. If resolution changes architecture or public behavior, escalate to Sol.

## Terra unavailable

Sol may assume coordination only through an explicit takeover/recovery procedure supported by the current Orca runtime. Do not run two active coordinators for the same execution namespace.

## Sol unavailable

Terra may continue only work that is clearly within an already approved plan. Architecture-changing or requirement-changing decisions remain blocked until Sol or Human authority is available.

## Heartbeat

Long-running workers should provide heartbeat/status when the injected lifecycle contract requests it. Heartbeat proves liveness, not completion.
