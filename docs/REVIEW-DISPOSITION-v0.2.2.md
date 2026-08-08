# v0.2.2 Review Disposition

This release applies the remaining governance-hardening recommendations from the v0.2.1 review.

| Review concern | v0.2.2 disposition |
|---|---|
| Fingerprint generation was too informal | Terra is now the canonical owner; semantic fingerprint format and Issue Identity Record are schema-backed. |
| Agents could rename the same issue | Fingerprint changes require prior fingerprint + explicit identity-change reason + material identity difference. |
| Material evidence was semantically weak | Evidence delta is now a typed closed set; repeated confirmation is excluded by policy and cannot be encoded as a valid delta kind. |
| Stagnation counter was mostly policy | Decision Progress Record now carries cycle count, previous escalation/decision provenance, stable decision-question keys, and schema-enforced stagnation state. |
| Rephrasing decision questions could evade comparison | Terra maintains a stable `decision_question_key`; stagnation uses the key rather than free-form wording. |
| Plan → Orca Task mapping needed more precision | Task Contract now distinguishes execution, review, targeted-validation, and SWARM investigation tasks. |
| Review task semantics needed clarity | Independent review is a separate Task with `review_of_task_id` and distinct agent/session/dispatch. |
| Pydantic and JSON Schema drift risk | All JSON Schemas are generated from Pydantic models and tested for exact alignment. |
| No real-Orca E2E proof yet | Explicit proof checklist and an intentionally unverified baseline file were added; v0.2.2 makes no E2E claim. |

## Deliberately not implemented

- No custom worker/process/session state machine.
- No mirrored Orca Task/Dispatch database.
- No automated semantic classifier that decides whether two fingerprints are truly the same issue; Terra remains accountable for that judgment, with audit records and anti-evasion rules.
- No claim of target-environment Orca compatibility until the real proof is executed.
