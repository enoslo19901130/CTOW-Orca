# ADR-0002 — Bound Decision Revalidation and Require Evidence Delta

- Status: Accepted
- Version: CTOW 0.2.1
- Date: 2026-08-08

## Context

Hierarchical agent teams can waste large amounts of reasoning tokens when a Worker reports a problem, Terra escalates it, and Sol repeatedly re-validates the same repository facts without changing the decision state. Repeating the same evidence with a stronger model does not guarantee progress and can create a costly loop.

## Decision

CTOW uses stable `issue_fingerprint` values and durable Decision Records. Once Sol disposes an issue, the same fingerprint may be reopened only with material evidence delta, a failed acceptance criterion after applying the decision, or the result of one explicitly requested bounded targeted validation.

Sol receives a compressed Decision Brief rather than full Worker transcripts by default.

For a blocking escalation Sol must choose one progress action:

1. `DECIDE`;
2. `REQUEST_TARGETED_EVIDENCE`;
3. `REVISE_PLAN`;
4. `ESCALATE_HUMAN`.

`REQUEST_TARGETED_EVIDENCE` is limited to one attempt and must define a hypothesis, method, success criterion, failure criterion, and expected decision impact.

Two consecutive cycles with the same fingerprint, no material evidence delta, and the same unresolved decision question are classified as stagnation. Further same-path validation stops.

## Consequences

Positive:

- reduces repeated high-cost Sol reasoning;
- converts escalation into a decision process rather than a recursive investigation;
- makes prior decisions reusable and auditable;
- forces validation requests to be falsifiable and bounded.

Tradeoffs:

- a poor early Decision Record can constrain later work until new evidence appears;
- Terra must perform better evidence compression and fingerprint deduplication;
- governance artifacts under `.ctow/decisions` become important project evidence.

## Rule for future agents

Do not bypass this rule by renaming the same issue, starting a fresh Luna session, or requesting another generic “full review.” New work must add material evidence or test a materially different hypothesis.
