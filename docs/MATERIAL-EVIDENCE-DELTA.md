# Material Evidence Delta

A material evidence delta must change the **decision-relevant information state**. Merely producing more volume is not progress.

Accepted delta classes:

- `changed_observable` — a previously asserted observable is now different;
- `new_failure_mode` — a distinct failure mode changes the diagnosis;
- `invalidated_hypothesis` — a bounded test falsifies a live hypothesis;
- `changed_decision_space` — an option becomes feasible/infeasible;
- `acceptance_failure` — applying a decision fails an acceptance criterion;
- `targeted_validation_result` — the one bounded validation requested by Sol returns;
- `new_constraint` — a previously unknown binding constraint is discovered;
- `new_reproduction_condition` — a new condition materially changes reproducibility/causality.

The following are explicitly **not material**:

- another worker agrees;
- another file repeats the same fact;
- the same test is re-run with the same result;
- the issue is reworded;
- a broader scan reaches the same conclusion;
- a longer explanation of unchanged evidence.

Every delta entry must include evidence references and explain its `decision_impact`.
