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

### Runtime profile enforcement

`config/agents.yaml` is policy input, not a prompt-time suggestion. The single
CTOW compiler maps each role's profile to explicit Codex arguments before Orca
creates the terminal:

| CTOW field | Codex argument | Effective receipt field |
|---|---|---|
| `model` | `--model <id>` | `model` |
| `reasoning_effort` | `-c model_reasoning_effort=<value>` | `reasoning_effort` |
| `fast_mode: false` | enforced by CTOW policy (no Fast-on launch) | `fast_mode: false` |
| `full_access: true` | `--sandbox danger-full-access` | `sandbox` |
| `full_access: false` | `--sandbox workspace-write` | `sandbox` |
| `auto_approve: true` | `--ask-for-approval never` | `approval` |
| `auto_approve: false` | `--ask-for-approval on-request` | `approval` |

`ctow-start --dry-run` exposes the complete Terra `terra_launch` object,
including `argv`, `requested_policy`, and `expected_effective_policy`. An
actual start must verify the structured receipt returned by that same Orca
`run-create`; the required model, effort, Fast OFF, sandbox, and approval
values must all come from one explicit effective-policy receipt subtree.
Missing or mismatched values are typed fail-closed errors; a successful
`run-create` alone is not evidence that execution started.

Create the execution Run once, then create all independent tasks before starting workers.

```bash
orca orchestration run-create --objective "<project execution objective>" --json
orca orchestration task-create --spec "<task A contract>" --json
orca orchestration task-create --spec "<task B contract>" --json
```

Start Luna workers using Orca's supervised worker path when the installed
Orca version can express and receipt all required permission fields:

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

Read the launch receipt and verify the effective model, effort, Fast OFF,
sandbox, and approval. CTOW policy forbids silent model/effort downgrade or
permission elevation/downgrade.

If `worker-start --help` does not expose sandbox/approval launch preferences,
use the Orca-authorized custom-terminal compatibility path, preserving formal
Task/Dispatch provenance:

```bash
orca terminal create --worktree new-child --command "<compiled Luna Codex argv>" --json
orca terminal wait --for tui-idle --json
# verify effective model/effort/fast_mode:false/sandbox/approval from the Orca receipt
orca orchestration dispatch --inject --task <task_id> --to <terminal_id> --json
```

The custom terminal is an Orca terminal, not a CTOW process supervisor. The
injected Dispatch remains the source of the Task contract, Dispatch identity,
heartbeats, questions, escalation, and `worker_done` lifecycle. Do not replace
it with an untracked terminal prompt. The Luna Worker and Independent Reviewer
both consume the Luna profile; a reviewer still requires a distinct
agent/session/Dispatch identity.

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

## Human gates remain independent

Codex `auto_approve` controls local tool prompts only. It does not authorize a
destructive production change, credentials/account use, external state change,
or an architecture decision requiring an owner preference. Those CTOW Human
gates remain mandatory and are evaluated independently of the local Codex
approval policy.
