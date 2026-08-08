# ADR-0003 — Canonical Issue Identity and Decision Progress Ledger

Status: Accepted

## Context

Anti-stagnation controls can be bypassed if agents rename the same issue or claim weak evidence as a material delta. Repeated high-reasoning review then resumes under a new label.

## Decision

1. Terra owns canonical issue identity.
2. Canonical fingerprints use semantic `domain-conflict_class-stable_subject` form.
3. Fingerprint changes require explicit material identity-change evidence.
4. Material evidence delta uses a closed set of decision-relevant kinds; repeated confirmation is excluded.
5. Every issue reaching Sol carries a Decision Progress Ledger with cycle count and stagnation state.
6. At cycle >=2 with the same decision question and no material delta, further targeted validation is forbidden.

## Consequences

CTOW favors decisive progress over recursive consensus gathering. Some borderline identity/evidence judgments remain semantic and therefore rely on Terra/Sol discipline, but they are now explicit, auditable, schema-backed contracts.
