# Real-Orca E2E Proof Checklist

> This repository does **not** claim this proof has been executed in CI. Run it in the target Orca installation and record the exact Orca version/commit and actual CLI receipts.

The next operational milestone is a real proof of:

1. Terra creates/binds an Orca Run.
2. Terra creates a validated Task Contract and corresponding Orca Task.
3. Terra starts a Luna Codex worker using the installed Orca orchestration command.
4. Luna reports `worker_done`; Terra receives and accepts it.
5. A second task forces Luna to send an escalation/question.
6. Terra canonicalizes the issue, consults `.ctow/issues/`, `.ctow/decisions/`, and `.ctow/decision-progress/`, then sends a compressed brief to Sol only if needed.
7. Sol records one progress action.
8. If targeted validation is chosen, Terra dispatches exactly one bounded validation task and returns only the resulting evidence delta.
9. A high-risk execution task receives an independent review task from a different Luna agent/session/dispatch.
10. A SWARM proof starts three independent Luna investigations and keeps reports isolated until Terra synthesis.

After execution, update `docs/ORCA-VERIFIED-BASELINE.md` with the observed commands/receipts. Until then, installed Orca help/skills remain authoritative.
