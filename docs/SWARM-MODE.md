# SWARM Mode

SWARM is for difficult investigation where independent hypotheses are more valuable than immediate parallel coding.

## Entry criteria

Terra may select SWARM when:

- root cause is unclear;
- concurrency/protocol/state bugs are suspected;
- previous attempts failed;
- multiple plausible architecture explanations exist;
- independent reproduction paths are valuable.

## Phase A — Independent investigation

Terra dispatches up to three Luna workers with the same problem statement but different optional investigation focus.

During this phase:

- workers must not read other workers' reports;
- workers must not receive other workers' reasoning;
- workers should avoid overlapping writes unless explicitly assigned as competing implementations;
- each worker produces evidence and a hypothesis independently.

## Phase B — Terra synthesis

After all independent investigations settle, Terra compares:

- reproduced symptoms;
- root-cause hypotheses;
- evidence quality;
- proposed fix scope;
- unresolved uncertainty.

## Phase C — Decision

If evidence converges and the fix remains inside the approved plan, Terra dispatches implementation.

If findings materially conflict or require architecture change, Terra escalates the synthesis to Sol.

## SWARM is not voting

Three workers agreeing does not override Sol's architecture authority. Consensus is evidence, not authority.
