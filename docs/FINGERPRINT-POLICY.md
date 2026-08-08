# Canonical Issue Fingerprint Policy

## Purpose

Prevent semantic renaming from bypassing decision history and anti-stagnation limits.

## Authority

- Luna may propose a **provisional** fingerprint when first reporting a problem.
- Terra owns the **canonical** fingerprint and must canonicalize an issue before it reaches Sol.
- Sol consumes the canonical identity; Sol does not rename it to reopen investigation.

## Canonical form

Use lowercase slug form:

`{domain}-{conflict_class}-{stable_subject}`

Example: `auth-contract-authstate`

The three parts should identify:

1. `domain` — affected subsystem;
2. `conflict_class` — stable problem class, not a symptom sentence;
3. `stable_subject` — the contract/component whose decision is blocked.

## Same issue — fingerprint MUST stay unchanged

These do not create a new identity:

- wording changed;
- another Luna reproduced the problem;
- another file confirms the same fact;
- the same test was re-run with the same outcome;
- another model/agent agrees;
- a full-repository rescan reaches the same conclusion.

## New identity

A fingerprint may change only when the **problem identity materially changes**, e.g.:

- root cause changes;
- the affected contract changes;
- the decision question changes materially;
- new evidence proves the prior issue was actually a different failure class.

A changed identity must record `previous_fingerprint`, `identity_change_reason`, and `material_identity_difference`.

Terra stores canonical identities in `.ctow/issues/` and checks aliases/history before escalating.
