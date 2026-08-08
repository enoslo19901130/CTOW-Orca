# Issue Escalation Contract

## Direction

Escalation moves exactly one authority level upward:

`Luna → Terra → Sol → Human`

## Identity

- Luna may propose a provisional issue fingerprint.
- Terra owns canonical fingerprint creation/reuse before escalation reaches Sol.
- Terra must search prior issue identities, decisions, escalations, and progress ledgers before treating a problem as new.
- Renaming the same conflict is prohibited. See `FINGERPRINT-POLICY.md`.

## Required escalation evidence

A structured escalation includes:

- escalation ID;
- issue fingerprint and canonicalization status;
- cycle count and previous provenance when applicable;
- severity / blocking state;
- concise summary;
- evidence references;
- attempted actions;
- falsified hypotheses;
- typed material evidence delta;
- exact decision required;
- bounded options and recommendation.

## Materiality

More evidence volume is not automatically new evidence. Another agreeing worker, another same-fact file, repeated same-result test, or broader scan is not material. See `MATERIAL-EVIDENCE-DELTA.md`.

## Terra → Sol gate

Before escalation to Sol, Terra must:

1. canonicalize/reuse fingerprint;
2. consult `.ctow/issues/`, `.ctow/decisions/`, `.ctow/escalations/`, `.ctow/decision-progress/`;
3. separate unchanged facts from material delta;
4. update cycle count and Decision Progress Ledger;
5. detect stagnation;
6. send a compressed decision brief rather than raw worker transcript.

If stagnation is detected, the brief must not invite more validation; Sol must decide/revise/escalate Human.
