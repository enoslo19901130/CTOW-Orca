# CTOW Command Entry Points

CTOW provides command entry points for governance intake and the handoff into Orca. They are thin adapters, not a second execution runtime.

## Install

```bash
python -m pip install -e .
```

This installs a unified command and three convenience aliases:

```text
ctow plan   = ctow-plan
ctow start  = ctow-start
ctow status = ctow-status
```

## Required operating order

Use this decision rule in every scenario:

```text
Status or handover question → ctow status
New requirement             → ctow-plan "<goal>"
Approved Plan only          → ctow-start --plan <PLAN.yaml>
```

`ctow status` comes first when inspecting existing work because Orca—not chat history or `.ctow/`—owns execution state. `ctow-plan` records intake but does not approve a Plan. `ctow-start` must never be used as a shortcut around Sol approval.

## Plan intake

```bash
ctow-plan "Add API key management"
# or
ctow plan "Add API key management"
```

The command writes a timestamped YAML request under `.ctow/requests/`. The request contains the goal and a Sol-ready prompt. It does **not** claim that an approved Plan exists and does not start an Orca Run.

Give the generated `sol_prompt` to Sol. Sol performs discovery, writes the approved Plan under `.ctow/plans/`, and validates it:

```bash
ctow-guard validate-plan .ctow/plans/PLAN-API-KEYS.yaml
```

Use `--output` to choose a deterministic request path:

```bash
ctow-plan "Add API key management" --output .ctow/requests/api-keys.yaml
```

Existing files are never overwritten.

## Start an approved Plan

Preview the action first:

```bash
ctow-start --plan .ctow/plans/PLAN-API-KEYS.yaml --dry-run
```

Create the authoritative Orca Run:

```bash
ctow-start --plan .ctow/plans/PLAN-API-KEYS.yaml
# or
ctow start --plan .ctow/plans/PLAN-API-KEYS.yaml
```

`ctow-start` performs these bounded actions:

1. validates the CTOW repository config;
2. validates the Plan schema and policy constraints;
3. verifies that the Orca runtime is reachable;
4. invokes `orca orchestration run-create --objective <plan.goal> --json`;
5. returns the Orca receipt and tells Terra to create the Task DAG and supervised Dispatches.

It does not create a shadow Run/Task database, start Luna directly, or poll Worker terminals.

## Query status

```bash
ctow status
# or
ctow-status
```

Status combines read-only information from the authoritative Orca runtime with local governance artifacts:

- Orca app/runtime readiness;
- the Run bound to the current coordinator terminal, when present;
- available Orca Runs;
- planning requests under `.ctow/requests/`;
- valid and invalid Plans under `.ctow/plans/`.

The output is JSON so both a Human and a Codex Agent can inspect the same receipt. Status does not persist or mirror Orca state.

## Start by exact goal

```bash
ctow-start "Add API key management"
```

This form searches `.ctow/plans/*.yaml` for a validated Plan whose `goal` exactly matches. It starts only when there is one match. With no match, run `ctow-plan` and complete Sol planning first. With multiple matches, select one explicitly using `--plan`.

It is a lookup convenience, not permission to start a new unplanned goal.

## Failure behavior

Commands exit with code `2` for invalid input, config, Plan, missing Orca, or failed Orca operations. `run-create` output is accepted only when Orca exits successfully and returns JSON. An unknown or failed mutation result is surfaced rather than retried automatically.

## Boundary

The commands intentionally stop at the Terra handoff. Automating Plan generation requires an actual Sol agent, and Task/Worker supervision belongs to Terra using the version-matched Orca orchestration skill. See [ADR-0004](adr/ADR-0004-CTOW-COMMAND-ENTRY-POINTS.md).
