> **ORCA CLI COMPATIBILITY WARNING**
>
> Command examples in this repository are **verified design examples, not a permanent Orca API contract**. Orca orchestration is experimental and may change. Before execution, use the installed `orca --help`, `orca orchestration --help`, and Orca orchestration skill as the authoritative syntax/lifecycle contract. CTOW must never preserve stale example syntax over the installed Orca runtime.

# Orca Integration Contract

CTOW v0.2 is designed around Orca's structured orchestration layer rather than a custom worker launcher.

## Required Orca capabilities

The template assumes the installed Orca runtime supports supervised orchestration concepts including:

- Run
- Task
- Task dependencies
- Dispatch
- `worker-start`
- `worker_done`
- `question` / reply
- `escalation`
- `heartbeat`
- coordinator `check` and acknowledgement
- worktree-backed agent terminals

The orchestration feature may need to be enabled under Orca Experimental settings.

## Preflight

```bash
orca status --json
orca orchestration run-list --json
codex --version
git --version
```

Do not claim CTOW supervised orchestration is available until those runtime checks succeed.

## Terra worker launch pattern

Create the execution Run once, then create all independent tasks before starting workers.

```bash
orca orchestration run-create --objective "<project execution objective>" --json
orca orchestration task-create --spec "<task A contract>" --json
orca orchestration task-create --spec "<task B contract>" --json
```

Start Luna workers using Orca's supervised worker path:

```bash
orca orchestration worker-start \
  --task <task_id> \
  --worktree new-child \
  --name <worker_name> \
  --agent codex \
  --model <luna_model_id> \
  --effort max \
  --setup run \
  --json
```

Read the launch receipt and verify the effective model/effort. CTOW policy forbids silent effort downgrade.

## Coordinator wait loop

```bash
orca orchestration check \
  --wait \
  --types worker_done,escalation,question \
  --timeout-ms 900000 \
  --json
```

Process the full delivery before acknowledging it. Timeouts are checkpoints, not failures.

## Worker completion

The injected supervised worker lifecycle should provide the exact task/dispatch IDs. Worker reports completion using Orca lifecycle messaging rather than writing a CTOW state database.

## Worker reuse

If the same Luna session immediately receives another Task, Terra may reuse the existing worker terminal using Orca's terminal/dispatch reuse path. Otherwise release the settled worker using Orca's worker-release lifecycle.

## Worktrees

Prefer a separate worktree for independent write tasks. Read-only investigation may share a current workspace only when concurrent mutation is impossible.

Orca owns the physical worktree lifecycle. CTOW owns the policy deciding when isolation is mandatory.

## Skills

CTOW's project-local role skills live in `.agents/skills`. They are behavioral policy. Orca's own orchestration skill remains the authoritative command-level guide when syntax or lifecycle behavior differs from this template.

## Compatibility rule

If a current Orca version changes CLI syntax, follow the current Orca skill/help output and update CTOW documentation. Do not preserve stale syntax merely to match this repository.
