# Source Notes

CTOW v0.2.x was redesigned after reviewing the current `stablyai/orca` repository.

Reference repository:

- https://github.com/stablyai/orca

Key source areas reviewed:

- `skill-guides/orchestration.md` — structured coordination, Run/Task/Dispatch, `worker-start`, worker lifecycle messages, questions, escalation, heartbeats, worker reuse/release, coordinator wait behavior.
- `src/cli/handlers/worktree.ts` — worktree creation, parent lineage, startup agent/prompt handling.
- `src/cli/handlers/skills.ts` — Orca skill discovery/install behavior and shared `.agents/skills` location.
- `src/shared/mcp-config.ts` and related MCP settings code — confirms Orca can coexist with MCP without requiring CTOW to use MCP as its worker runtime.

Source snapshot observed during the v0.2 architecture review included commit references around:

`ce20a109dab68a3d2b4844e204eb8a0454069a99`

Orca changes quickly. Runtime syntax in this repository is therefore illustrative where explicitly stated. The installed Orca help/skill guide is authoritative for current CLI grammar.

## v0.2.2 verification status

The Orca-native design was reviewed against Orca source/skill behavior available during the 2026-08-08 design session. CTOW examples remain version-sensitive. This repository does not yet claim a CI-automated real-Orca end-to-end run; the next operational milestone is the real-Orca proof in `ORCA-E2E-PROOF.md`; until recorded in `ORCA-VERIFIED-BASELINE.md`, no target-environment E2E verification is claimed.
