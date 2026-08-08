# Terra Runbook Example

> Orca command syntax is version-sensitive. Verify the installed Orca help/orchestration skill before execution.

1. Validate Plan and Task Contract with `ctow-guard`.
2. Create/bind the Orca Run.
3. Create ready Orca Tasks from validated CTOW Task Contracts.
4. Start independent Luna workers with Orca supervised orchestration.
5. Wait for `worker_done`, `escalation`, and `question`; timeout is not failure.
6. On escalation:
   - search `.ctow/issues/` for semantic identity/aliases;
   - assign/reuse the Terra-owned canonical fingerprint;
   - inspect prior `.ctow/decisions/`, `.ctow/escalations/`, and `.ctow/decision-progress/`;
   - increment cycle count and separate unchanged facts from typed material evidence delta;
   - write/update Issue Identity + Decision Progress records;
   - resolve locally or send Sol a compressed brief.
7. If the ledger indicates stagnation, do not commission more validation. Sol may only decide, revise the plan, or escalate Human.
8. If Sol requests targeted validation, create exactly one bounded `targeted_validation` Task and return only the result/evidence delta.
9. For high/critical execution, create a separate independent review Task using a different Luna agent/session/dispatch.
10. Integrate only after acceptance and review gates pass.
