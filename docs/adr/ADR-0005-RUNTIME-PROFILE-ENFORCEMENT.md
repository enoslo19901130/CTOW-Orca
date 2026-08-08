# ADR-0005 — Enforce Runtime Profiles at Orca Bootstrap

- Status: Accepted
- Version: CTOW Unreleased
- Date: 2026-08-08

## Context

CTOW role profiles declare model, reasoning effort, Fast OFF, sandbox, and
local approval intent, but the previous handoff only documented model and
effort. Terra could therefore create a Run while its Codex bootstrap silently
used a different sandbox or interactive approval policy. Orca's `worker-start` may
also lack flags for the complete Luna policy in a particular installed
version.

## Decision

CTOW has one pure profile-to-Codex compiler. It emits explicit model, effort,
sandbox, and approval arguments for Sol, Terra, Luna, and the Luna Reviewer,
and rejects any profile that does not set Fast OFF.
True permissions map to `danger-full-access` and `never`; false permissions
map to non-elevated concrete policies and are never promoted.

Every required effective policy field (including `fast_mode: false`) must be
present in one explicit effective-policy subtree of the actual Orca bootstrap
receipt and match the requested policy. CTOW never merges requested, sibling,
or unrelated receipt envelopes. Missing or mismatched values raise a typed
fail-closed error. `ctow-start --dry-run` exposes the complete Terra launch
contract; an actual start reports `execution_started` only after verified
Terra bootstrap from that same Orca receipt.

When `worker-start` cannot express sandbox or approval, Terra may use an Orca
custom terminal with the compiled argv, verify the effective receipt, and
inject the formal Task/Dispatch. This remains an Orca terminal and does not
create a CTOW process supervisor, PTY manager, or shadow execution database.

Codex local auto-approval remains independent from CTOW Human gates. It only
controls local tool prompts and cannot authorize destructive production work,
credential/account use, external state changes, or owner-level architecture
decisions.

## Consequences

Positive:

- profile intent is translated once and is auditable in receipts;
- sandbox/approval downgrades fail before CTOW claims execution started;
- version-specific Orca worker capabilities have an explicit, provenance-
  preserving fallback;
- Orca remains the single runtime source of truth.

Tradeoffs:

- a real Orca bootstrap receipt is required before start success;
- the installed Orca syntax and receipt shape remain version-sensitive;
- a Run may exist in Orca when bootstrap fails and requires normal Orca
  cleanup/recovery, but CTOW reports it as not started.

## Non-goals

- implementing a custom Codex launcher, PTY supervisor, or process manager;
- parsing interactive TUI text as a permanent runtime API contract;
- bypassing CTOW planning, Task/Dispatch provenance, or Human decision gates.
