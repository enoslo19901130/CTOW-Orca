# Independent Review Policy

Independent review is a session-separation control for high-risk work.

## Mandatory identity separation

The reviewer must differ from the author in all applicable identities:

- agent/session identity;
- terminal identity;
- Dispatch identity.

A worker cannot “change hats” in the same session and count as independent review.

## Initial evidence

Prefer to give the reviewer:

1. Task Contract;
2. acceptance criteria;
3. final diff;
4. tests/results;
5. relevant repository state.

Do not initially provide the author's full reasoning transcript unless the reviewer requests it after independent analysis.

## Reviewer authority

Reviewer may inspect the whole project and run tests. Review-only mode should not silently edit the implementation. Findings return to Terra, which dispatches corrections or escalates architecture issues to Sol.

## Outcome

Use `PASS`, `CONDITIONAL_PASS`, or `FAIL`, plus findings with severity and evidence.
