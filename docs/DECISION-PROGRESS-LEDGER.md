# Decision Progress Ledger

Each canonical issue that reaches Sol receives a ledger under `.ctow/decision-progress/`.

The ledger exists to make repeated reasoning visible before tokens are spent.

Required fields include:

- canonical `issue_fingerprint`;
- `cycle_count`;
- current/previous escalation IDs;
- previous decision ID when applicable;
- current and previous decision question plus stable semantic question keys;
- unchanged facts;
- material evidence delta;
- `stagnation_detected`;
- allowed next actions.

## Stagnation rule

At cycle 2 or later, if the canonical `decision_question_key` is unchanged and there is no material evidence delta, the ledger MUST mark stagnation.

Once stagnating, `REQUEST_TARGETED_EVIDENCE` is no longer legal. The next action must be one of:

- `DECIDE`;
- `REVISE_PLAN`;
- `ESCALATE_HUMAN`.

Terra updates/checks this governance record before another escalation to Sol. The ledger is not an Orca runtime mirror.
