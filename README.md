# CTOW — Codex Team Orchestration Workflow

English | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

> Version 0.2.2 · Orca-native development template

CTOW is a governance workflow for running a hierarchical team of Codex agents in Orca. It defines who may plan, schedule, implement, review, and decide, while Orca remains the authoritative execution runtime.

> **Compatibility notice:** Orca orchestration is version-sensitive and experimental. Examples here describe the reviewed baseline; the installed Orca CLI help and orchestration skill are authoritative. CTOW has policy and unit validation, but does not yet claim automated real-Orca end-to-end coverage in CI.

## What CTOW provides

CTOW turns a project request into a governed delivery chain:

```text
USER → SOL → TERRA → LUNA → RESULT
        plan   schedule  build/test
```

- **User** owns product intent, constraints, and human decisions.
- **Sol (Architect)** owns architecture, plans, major decisions, and final review.
- **Terra (Commander)** owns the Orca Run, Task DAG, dispatch, integration, and canonical issue identity.
- **Luna (Worker)** performs bounded implementation, testing, and reporting.
- **Luna Reviewer** independently reviews high-risk work in a different session and Dispatch.
- **Orca** owns worktrees, terminals, workers, Tasks, Dispatches, and execution state.
- **CTOW** owns governance rules and evidence; it does not replace Orca's runtime.
- **Runtime profiles** are compiled centrally into Codex launch arguments and
  must be proven by requested/effective Orca receipts before bootstrap is
  reported as started.

Decisions flow downward; uncertainty and conflicts flow upward:

```text
Decisions: USER → SOL → TERRA → LUNA
Issues:    LUNA → TERRA → SOL → USER
```

Full filesystem access is not full authority. Each role stays within its assigned responsibility.

## Why use it

Opening several agent terminals is easy; keeping them aligned is not. CTOW adds:

- explicit authority and handoff boundaries;
- supervised worker dispatch through Orca;
- dependency-aware Work Packages and Tasks;
- independent review for high-risk changes;
- structured escalation and human decision gates;
- stable issue fingerprints and bounded validation to prevent repeated, same-evidence reasoning loops;
- schemas and `ctow-guard` validation for governance artifacts.

CTOW deliberately does **not** implement a PTY manager, process supervisor, worktree manager, task database, or second execution state machine. See [ADR-0001](docs/adr/ADR-0001-ORCA-AUTHORITATIVE-RUNTIME.md).

## Requirements and preflight

You need Git, Codex CLI, Orca, Python 3.10+, and an Orca runtime with orchestration enabled where required.

```bash
python -m pip install -e .
python scripts/preflight.py
python scripts/verify_skills.py
```

The model names in `config/agents.yaml` express policy intent. Verify the effective model and reasoning effort reported by the installed Orca/Codex runtime; CTOW must not silently downgrade them.

Runtime verification also requires Fast OFF (`fast_mode: false`) and covers the
concrete sandbox and approval policy.
`full_access: true` compiles to `--sandbox danger-full-access` and
`auto_approve: true` compiles to `--ask-for-approval never`; false values compile
to non-elevated policies and are never promoted. A launch receipt must expose
the requested and effective model, effort, Fast OFF, sandbox, and approval
values from one explicit effective-policy subtree returned by Orca.

## Command entry points

Always select the command by intent:

```text
Inspect existing work → ctow status
Submit a new goal     → ctow-plan "<goal>"
Start approved work   → ctow-start --plan <PLAN.yaml>
```

Query authoritative Runtime state and local governance progress first when inspecting or taking over work:

```bash
ctow status
# equivalent: ctow-status
```

For a new requirement, create a planning request:

```bash
ctow-plan "Add API key management"
```

This records a planning request and produces a Sol-ready prompt. After Sol writes and validates an approved Plan, preview and start its authoritative Orca Run:

```bash
ctow-start --plan .ctow/plans/PLAN-API-KEYS.yaml --dry-run
ctow-start --plan .ctow/plans/PLAN-API-KEYS.yaml
```

`ctow-start --dry-run` includes the complete Terra `terra_launch` policy and
argv. An actual start is considered execution-started only after Orca returns a
machine-verifiable Terra bootstrap receipt; a missing or mismatched receipt is
a typed fail-closed error even if Orca already created the Run.

The unified forms `ctow plan` and `ctow start` are equivalent. `ctow-start "<exact goal>"` can resolve one matching validated Plan under `.ctow/plans/`; it is only a lookup convenience and never skips planning. These commands stop at the verified Terra handoff and do not implement a second scheduler or Worker runtime. See [Command Entry Points](docs/COMMANDS.md).

## Start a project

The normal entry point is the User speaking to Sol. Provide the goal, constraints, authoritative documents, acceptance criteria, and anything that must not change. Sol performs discovery and planning before implementation; Terra then maps the approved plan into Orca Tasks and dispatches Luna workers.

### Recommended request template

```yaml
project_goal:
background:
current_state:
desired_state:
must_have:
must_not_change:
known_constraints:
known_risks:
authoritative_documents:
acceptance_criteria:
out_of_scope:
human_decisions_already_made:
notes:
```

Not every field is required. A useful opening prompt is:

```text
Act as the CTOW Sol Architect for this repository.

Read AGENTS.md, the Sol skill, relevant ADRs and policy, existing .ctow/
governance evidence, and the repository state.

Goal: [describe the outcome]
Constraints: [what must or must not change]
Acceptance: [how completion will be verified]

Begin with discovery and planning, not implementation. Define scope, risks,
acceptance criteria, Work Packages, dependencies, execution profile, worker
demand, and independent-review requirements. Ask the Human only when missing
information would materially change product intent, architecture boundaries,
or acceptance criteria. Validate the Plan, then hand it to Terra for execution.
```

### End-to-end flow

```text
User request
  → Sol discovery, architecture, risks, acceptance, Work Packages
  → validated CTOW Plan
  → Terra creates Orca Run, Task DAG, worktrees, and Dispatches
  → Luna implements, builds, tests, and reports
  → independent Luna review when risk requires it
  → Terra integrates and checks acceptance
  → Sol performs final architecture and plan-compliance review
  → User receives results, decisions, evidence, residual risks, and deferred items
```

## Common operating scenarios

### 1. New project

Ask Sol to establish product boundaries, core entities, security, persistence, API/UI boundaries, deployment assumptions, risks, and acceptance criteria before producing the Work Package DAG. Use this when architecture does not yet exist.

### 2. Feature in an existing system

Name the affected domain and invariants. Sol first maps existing ownership, transaction and compatibility boundaries, then plans the change. For example, a trading feature should explicitly protect account ownership, inventory consistency, rollback, concurrency, and old data compatibility.

### 3. Intermittent bug with unknown root cause

Do not prescribe a fix. Ask Sol to define failure domains, falsifiable hypotheses, required evidence, and success/failure criteria. Terra may use `SWARM` to send up to three Luna workers down independent evidence paths, then synthesize their findings without majority voting.

### 4. Small fix with a known root cause

Use `SMALL` when scope is narrow and no architecture or shared contract changes are involved. The expected path is one Luna Worker performing confirmation, a minimal fix, a regression test, and focused validation.

### 5. Large refactor

State the invariants that cannot change and require incremental, buildable, reversible Work Packages. Protocol behavior, initialization order, shared state, compatibility, rollback, and regression coverage should be explicit. High-risk packages require independent review.

### 6. A preferred solution that is not yet a decision

Label it as a proposal. Sol should independently test its necessity, consistency model, failure modes, operational cost, latency, and simpler alternatives rather than treating preference as an approved architecture requirement.

### 7. Complete authoritative specifications

List the PRD, protocol, schema, API contract, and acceptance documents. Sol performs gap analysis and must preserve their intent. Human input is needed only for internal contradictions, impossible compatibility, or mutually incompatible acceptance criteria.

### 8. Security or data-integrity change

For authentication, authorization, billing, encryption, migrations, or ownership transfers, require independent review, rollback, regression tests, failure-mode analysis, auditability, and explicit security/integrity acceptance criteria.

## Execution profiles

| Profile | Luna Workers | Use case |
|---|---:|---|
| `SMALL` | 1 | Narrow fix or small, low-risk feature |
| `MEDIUM` | 2 | Cross-module work with moderate dependencies |
| `FULL` | 3 | Large feature/refactor with multiple Work Packages |
| `SWARM` | 3 | Independent investigation of a difficult unknown |

Profiles are scheduling policies, not models. In `SWARM`, workers investigate independently before Terra synthesizes results. See [SWARM mode](docs/SWARM-MODE.md).

## Escalation and decision progress

Luna reports local uncertainty to Terra. Terra resolves execution issues and escalates architecture or plan conflicts to Sol. Sol escalates product ambiguity, destructive choices, or owner-level trade-offs to the User.

Terra owns the canonical `issue_fingerprint` and consults `.ctow/issues/`, `.ctow/decisions/`, and `.ctow/decision-progress/` before sending Sol a compressed Decision Brief. Rewording, another agreeing worker, or rerunning the same test is not new evidence.

Sol may:

- `DECIDE`;
- request one bounded `REQUEST_TARGETED_EVIDENCE` experiment;
- `REVISE_PLAN`;
- `ESCALATE_HUMAN`.

When the same issue and decision question reach cycle 2 without a material evidence delta, further targeted validation is forbidden. See [Decision Efficiency](docs/DECISION-EFFICIENCY.md), [Fingerprint Policy](docs/FINGERPRINT-POLICY.md), and [Decision Progress Ledger](docs/DECISION-PROGRESS-LEDGER.md).

## Independent review

High-risk work must be reviewed by a separate Luna session:

```text
author_agent != reviewer_agent
author_session != reviewer_session
author_dispatch != reviewer_dispatch
```

The reviewer starts with the Task Contract, acceptance criteria, diff, test results, and repository evidence—not the author's full reasoning transcript. See [Independent Review](docs/INDEPENDENT-REVIEW.md).

## Validate governance artifacts

```bash
ctow-guard validate-config
ctow-guard validate-plan examples/PLAN-DEMO.yaml
ctow-guard validate-task examples/TASK-WP001.yaml
ctow-guard validate-worker-report examples/WORKER-REPORT-DEMO.yaml
ctow-guard validate-review examples/REVIEW-DEMO.yaml
ctow-guard validate-issue-identity examples/ISSUE-IDENTITY-DEMO.yaml
ctow-guard validate-escalation examples/ESCALATION-DEMO.yaml
ctow-guard validate-decision examples/DECISION-DEMO.yaml
ctow-guard validate-decision-progress examples/DECISION-PROGRESS-DEMO.yaml
```

## Repository map

| Path | Purpose |
|---|---|
| `AGENTS.md` | Entry rules for agents opening the repository |
| `.agents/skills/` | CTOW operator plus Sol, Terra, Luna, and independent-review role contracts |
| `config/` | Agent profiles and governance policy |
| `.ctow/` | Durable governance evidence, never a duplicate runtime database |
| `docs/adr/` | Architecture decisions |
| `docs/` | Workflow, escalation, review, recovery, and integration guides |
| `schemas/`, `examples/` | Governance schemas and valid examples |
| `src/ctow_guard/`, `tests/` | Validation package and policy tests |

## Project status

CTOW v0.2.2 is a governance-hardened, Orca-native development template. Role contracts, policies, schemas, examples, guard validation, and unit tests are present. Real-Orca end-to-end proof remains the next operational milestone; until [the proof checklist](docs/ORCA-E2E-PROOF.md) is executed and recorded in [the verified baseline](docs/ORCA-VERIFIED-BASELINE.md), runtime E2E verification is not claimed.

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Workflow](docs/WORKFLOW.md)
- [Orca integration](docs/ORCA-INTEGRATION.md)
- [Runtime profile enforcement](docs/adr/ADR-0005-RUNTIME-PROFILE-ENFORCEMENT.md)
- [Task Contract](docs/TASK-CONTRACT.md)
- [Command entry points](docs/COMMANDS.md)
- [Issue escalation](docs/ISSUE-ESCALATION.md)
- [Break-glass policy](docs/BREAK-GLASS.md)
- [Changelog](CHANGELOG.md)
