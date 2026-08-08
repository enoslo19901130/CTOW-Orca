# Changelog

## 0.2.2

- Make Terra the canonical issue-fingerprint authority; Luna may only propose provisional identity for new issues.
- Add semantic fingerprint format and audited identity-change contract to prevent rename-based anti-loop bypass.
- Replace free-form material evidence delta strings with typed decision-relevant evidence categories; repeated confirmation is explicitly non-material.
- Add Issue Identity Record and Decision Progress Ledger schemas/models/examples under `.ctow/issues/` and `.ctow/decision-progress/`.
- Enforce cycle provenance and stagnation: cycle >=2 + same decision question + no material delta must mark stagnation and forbids additional targeted validation.
- Add WorkerReport Pydantic model and generate every JSON Schema directly from the Pydantic source; add schema-alignment tests.
- Expand Task Contract with execution/review/targeted-validation/SWARM task types and explicit independent review-task linkage.
- Add Orca E2E proof checklist and an intentionally unverified baseline record; do not claim runtime verification until executed in the target environment.
- Add ADR-0003 for canonical issue identity and decision-progress governance.

## 0.2.1

- Add decision-efficiency / anti-stagnation protocol to prevent repeated same-evidence Sol validation loops.
- Require stable issue fingerprints and material evidence delta before reopening a decided issue.
- Add bounded targeted-validation contract with max one attempt per Sol request.
- Add durable governance evidence layout under `.ctow/` without duplicating Orca execution state.
- Add Task Contract model/schema/example and explicit WP → N Tasks / separate review Task mapping.
- Strengthen independent review to require different agent, session, and Dispatch identities.
- Expand `ctow-guard` for config consistency, Task, escalation, decision, break-glass, and Human-decision validation.
- Make Orca CLI compatibility warning prominent and state that automated real-Orca E2E is not yet in CI.

## 0.2.0

- Refactor CTOW into an Orca-native governance layer.
- Remove custom Python worker/runtime control plane.
- Add Orca-native role skills, SWARM, recovery, independent review, break-glass, and governance guard.
