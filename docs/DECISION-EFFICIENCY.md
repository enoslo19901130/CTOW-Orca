# Decision Efficiency and Anti-Stagnation Protocol

CTOW prevents an expensive failure mode: Luna → Terra → Sol escalates a problem, then the decision layer repeatedly reads the same evidence or commissions semantically identical verification without changing the decision state.

## Core rule: no information gain, no new loop

Every issue has a stable canonical fingerprint owned by Terra. Sol must read the compressed Decision Brief, Decision Record, and Decision Progress Ledger before requesting more work.

A prior decision can be reopened only when:

1. a typed **material evidence delta** exists;
2. applying the decision causes an acceptance failure; or
3. the single bounded targeted validation requested by Sol returns a result.

See `FINGERPRINT-POLICY.md` and `MATERIAL-EVIDENCE-DELTA.md`.

## Decision Brief, not transcript forwarding

Terra sends Sol only decision-relevant information:

- canonical fingerprint and cycle count;
- previous escalation/decision IDs;
- exact decision question and stable `decision_question_key`;
- unchanged facts that Sol does not need to rediscover;
- evidence references;
- actions attempted and hypotheses falsified;
- typed material evidence delta;
- bounded options and Terra recommendation.

Full worker reasoning/transcripts are not forwarded by default. Sol may request one specific artifact if its absence blocks the decision.

## Sol progress actions

For a blocking escalation, Sol chooses exactly one:

- `DECIDE`;
- `REQUEST_TARGETED_EVIDENCE` — one bounded experiment only;
- `REVISE_PLAN`;
- `ESCALATE_HUMAN`.

“Verify again”, “review everything again”, “ask another Luna the same question”, or “rescan the repository” are not valid dispositions.

## Bounded targeted validation

A request must specify hypothesis, method, success criterion, failure criterion, expected decision impact, and `max_attempts = 1`.

The result must return as `targeted_validation_result` (or another valid typed material delta), not as a new open-ended investigation.

## Stagnation detector

At cycle 2 or later, if the canonical fingerprint and decision question are unchanged and there is no material evidence delta, the workflow is stagnating.

At stagnation, further validation is forbidden. Sol must `DECIDE`, `REVISE_PLAN`, or `ESCALATE_HUMAN`.

## Fingerprint anti-evasion

Luna may suggest a provisional key. Terra canonicalizes it before Sol. Rewording, another worker agreement, repeated tests, or additional same-fact files do not justify a new fingerprint. Identity changes require explicit material identity-change evidence.

## Governance persistence

- `.ctow/issues/` — canonical issue identity/aliases;
- `.ctow/escalations/` — compressed escalation evidence;
- `.ctow/decisions/` — Sol/Human decisions;
- `.ctow/decision-progress/` — cycle/stagnation state.

These are governance records, not a duplicate Orca Task/Dispatch database.
